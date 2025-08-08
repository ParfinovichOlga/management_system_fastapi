import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)
from config import MODE, DATABASE_URL
from ..backend.db import Base
from app.main import app
from ..backend.db_depends import get_db
from ..routers.auth import get_current_user_strict
from ..routers.auth import bcrypt_context
from httpx import AsyncClient, ASGITransport
from datetime import date
from ..models import Task, User


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    assert MODE == 'TEST'

    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        async_engine, class_=AsyncSession,
        expire_on_commit=False
        )
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_get_session(db_session):
    async def _override():
        yield db_session
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


def override_current_user_manager():
    return {
        'username': 'test_user',
        'id': 1,
        'role': 'manager'
    }


def override_current_user():
    return {
        'username': 'test_user',
        'id': 1,
        'role': 'staff'
    }


def override_current_user_admin():
    return {
        'username': 'test_user',
        'id': 2,
        'role': 'admin'
    }


@pytest_asyncio.fixture(scope='function')
async def async_client():
    app.dependency_overrides[get_current_user_strict] = override_current_user
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture(scope='function')
async def async_public_client():

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture(scope='function')
async def async_client_admin():
    app.dependency_overrides[
        get_current_user_strict] = override_current_user_admin
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture(scope='function')
async def test_user(db_session):
    user = User(
        name='test_user',
        hashed_password=bcrypt_context.hash('test123'),
        email='test@example.com'
    )

    db_session.add(user)
    await db_session.commit()
    yield user


@pytest_asyncio.fixture(scope='function')
async def async_client_manager():
    app.dependency_overrides[
        get_current_user_strict
        ] = override_current_user_manager
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture(scope='function', autouse=True)
async def test_task(db_session):
    task = Task(
        description='Test task',
        deadline=date(2025, 8, 16)
    )

    db_session.add(task)
    await db_session.commit()
    yield task

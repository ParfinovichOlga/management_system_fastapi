import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)
from config import MODE, DATABASE_URL
from ..backend.db import Base
from app.main import app
from ..backend.db_depends import get_db


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

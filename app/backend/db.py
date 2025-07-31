from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker, AsyncSession
)

from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)

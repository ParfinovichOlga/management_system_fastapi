from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, AsyncSession
)

from sqlalchemy.orm import DeclarativeBase
from config import settings


class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

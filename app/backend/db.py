from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, AsyncSession
)

from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

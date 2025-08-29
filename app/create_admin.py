from sqlalchemy import select
from .models import User
from .backend.db import async_session
from passlib.hash import bcrypt
from config import config


async def create_super_admin():
    async with async_session() as session:
        result = await session.scalar(
            select(User).where(User.email == config.ADMIN_EMAIL)
        )
        if result:
            print(f"Admin user '{config.ADMIN_EMAIL}' already exists.")
            return

        hashed_password = bcrypt.hash(config.ADMIN_PASSWORD)
        admin_user = User(
            email=config.ADMIN_EMAIL,
            hashed_password=hashed_password,
            name=config.ADMIN_NAME,
            role="admin",
            is_active=True,
        )

        session.add(admin_user)
        await session.commit()
        print(f"Superadmin '{config.ADMIN_EMAIL}' created successfully.")

from sqlalchemy import select
from .models import User
from .backend.db import async_session
from passlib.hash import bcrypt
from config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME


async def create_super_admin():
    async with async_session() as session:
        result = await session.scalar(
            select(User).where(User.email == ADMIN_EMAIL))
        if result:
            print(f"Admin user '{ADMIN_EMAIL}' already exists.")
            return

        hashed_password = bcrypt.hash(ADMIN_PASSWORD)
        admin_user = User(
            email=ADMIN_EMAIL,
            hashed_password=hashed_password,
            name=ADMIN_NAME,
            role="admin",
            is_active=True
        )

        session.add(admin_user)
        await session.commit()
        print(f"Superadmin '{ADMIN_EMAIL}' created successfully.")

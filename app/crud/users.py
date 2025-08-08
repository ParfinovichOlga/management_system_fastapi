from ..models import User, Roles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from ..routers.auth import bcrypt_context


async def get_user(db: AsyncSession, id: int):
    user = await db.scalar(select(User).where(User.id == id))
    return user


async def get_user_by_email(db: AsyncSession, email: str):
    user = await db.scalar(select(User).where(User.email == email))
    return user


async def create_user(db: AsyncSession, name: str, email: str, password: str):
    await db.execute(insert(User).values(
            name=name, email=email,
            hashed_password=bcrypt_context.hash(password)
        ))
    await db.commit()


async def update_user(db: AsyncSession, id: int,
                      name: str = None, email: str = None,
                      password: str = None,
                      is_active: bool = None,
                      role: Roles = None,
                      ):
    user = await get_user(db, id)
    if not user:
        return None
    user.email = email if email else user.email
    user.hashed_password = bcrypt_context.hash(password) if password else \
        user.hashed_password
    user.name = name if name else user.name
    user.role = role if role else user.role
    user.is_active = is_active if is_active else user.is_active
    await db.commit()


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()

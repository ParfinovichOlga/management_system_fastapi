from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.abstract.user import UserRepository
from sqlalchemy import select, insert
from app.models import User
from app.schemas import CreateUser, UpdateUser


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, id: int):
        user = await self.db.scalar(select(User).where(User.id == id))
        return user

    async def get_user_by_email(self, email: str):
        user = await self.db.scalar(select(User).where(User.email == email))
        return user

    async def get_user_by_name(self, name: str):
        return await self.db.scalar(select(User).where(User.name == name))

    async def create_user(self, user: CreateUser):
        await self.db.execute(
            insert(User).values(
                name=user.name, email=user.email, hashed_password=user.password
            )
        )
        await self.db.commit()

    async def update_user(self, user: UpdateUser):
        db_user = await self.get_user(user.id)
        if db_user:
            db_user.email = user.email
            db_user.hashed_password = user.password
            db_user.name = user.name
            db_user.role = user.role
            db_user.is_active = user.is_active
            await self.db.commit()

    async def delete_user(self, user_id: int):
        user = await self.get_user(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()

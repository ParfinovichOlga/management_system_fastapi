from ..routers.auth import bcrypt_context
from app.repositories.abstract.user import UserRepository
from app.schemas import CreateUser, UpdateUser
from typing import List
from fastapi import HTTPException, status


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, id: int):
        return await self.repo.get_user(id)

    async def get_user_by_email(self, email: str):
        return await self.repo.get_user_by_email(email)

    async def get_get_user_by_name(self, name: str):
        return await self.repo.get_user_by_name(name)

    async def create_user(self, name: str, email: str, password: str):
        user = CreateUser(
            name=name, email=email, password=bcrypt_context.hash(password)
        )
        await self.repo.create_user(user)

    async def update_user(
        self,
        id: int,
        name: str = None,
        email: str = None,
        password: str = None,
        is_active: bool = None,
        role: str = None,
    ):
        user = await self.repo.get_user(id)
        if user:
            updated_user = UpdateUser(
                id=id,
                email=email if email else user.email,
                password=(
                    bcrypt_context.hash(password) if password else user.hashed_password
                ),
                name=name if name else user.name,
                role=role if role else user.role,
                is_active=is_active if not is_active is None else user.is_active,
            )
            await self.repo.update_user(updated_user)
        return None

    async def delete_user(self, user_id: int):
        user = await self.repo.get_user(user_id)
        if user:
            await self.repo.delete_user(user_id)

    async def check_users_list(self, users: List[int]):
        """
        Check if all users in the list exist by their IDs
        and are not already assigned to a team
        and that there is no more than one manager in the list.
        """
        manager_exists = False
        existing_users = []
        for id in users:
            user = await self.repo.get_user(id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with {id} id not found",
                )
            elif user.team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with {id} is already in {user.team} team",
                )
            elif user.role == "manager":
                if manager_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You try to add 2 managers at the team",
                    )
                manager_exists = True

            existing_users.append(user)
        return existing_users

    async def update_user_role(self, user_id: int, role: str):
        updated_user = await self.get_user(user_id)
        if updated_user:
            await self.update_user(id=user_id, role=role)

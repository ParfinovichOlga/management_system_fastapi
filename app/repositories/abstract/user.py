from abc import ABC, abstractmethod
from app.schemas import UserOut, CreateUser, UpdateUser


class UserRepository(ABC):
    """
    Defines the interface all UserRepository implementations must follow.
    """

    @abstractmethod
    async def get_user(self, id: int) -> UserOut:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserOut:
        pass

    @abstractmethod
    async def get_user_by_name(self, name: str) -> UserOut:
        pass

    @abstractmethod
    async def create_user(self, user: CreateUser) -> None:
        pass

    @abstractmethod
    async def update_user(self, user: UpdateUser) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int):
        pass

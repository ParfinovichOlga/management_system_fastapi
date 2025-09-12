from abc import ABC, abstractmethod
from app.models import Comment


class CommentRepository(ABC):
    """
    Defines the interface all CommentRepository implementations must follow.
    """

    @abstractmethod
    async def get_comment(self, id: int) -> Comment:
        pass

    @abstractmethod
    async def get_comment_with_author(self, id: int) -> Comment:
        pass

    @abstractmethod
    async def create_comment(self, task_id: int, user_id: int, text: str) -> None:
        pass

    @abstractmethod
    async def update_comment(self, id: int, text: str):
        pass

    @abstractmethod
    async def delete_comment(self, id: int):
        pass

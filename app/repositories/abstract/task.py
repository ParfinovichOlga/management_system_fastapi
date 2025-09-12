from abc import ABC, abstractmethod
from app.models import Task
from typing import List
from datetime import date, datetime


class TaskRepository(ABC):
    """
    Defines the interface all TaskRepository implementations must follow.
    """

    @abstractmethod
    async def get_task(self, task_id: int) -> Task:
        pass

    @abstractmethod
    async def get_task_with_comments(self, task_id: int) -> Task:
        pass

    @abstractmethod
    async def get_tasks(self) -> List[Task]:
        pass

    @abstractmethod
    async def get_user_tasks(self, user_id: int) -> List[Task]:
        pass

    @abstractmethod
    async def get_tasks_for_period(
        self, user_id: int, start: datetime, end: datetime
    ) -> List[Task]:
        pass

    @abstractmethod
    async def create_task(self, description: str, deadline: date):
        pass

    @abstractmethod
    async def update_task(
        self,
        task_id: int,
        description: str,
        deadline: date,
        status: str,
        assigned_to: int,
    ):
        pass

    @abstractmethod
    async def delete_task(self, task_id: int):
        pass

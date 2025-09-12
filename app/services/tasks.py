from ..models import Task, TaskStatus
from app.repositories.abstract.task import TaskRepository
from datetime import date
from typing import List


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    async def get_task(self, task_id: int) -> Task:
        return await self.repo.get_task(task_id)

    async def get_task_with_comments(self, task_id: int) -> Task:
        return await self.repo.get_task_with_comments(task_id)

    async def get_tasks(self) -> List[Task]:
        return await self.repo.get_tasks()

    async def get_user_tasks(self, user_id: int) -> List[Task]:
        return await self.repo.get_user_tasks(user_id)

    async def create_task(self, description: str, deadline: date):
        await self.repo.create_task(description, deadline)

    async def update_task(
        self,
        task_id: int,
        description: str = None,
        deadline: date = None,
        status: TaskStatus = None,
        assigned_to: int = None,
    ):
        return await self.repo.update_task(
            task_id, description, deadline, status, assigned_to
        )

    async def delete_task(self, task_id: int):
        task = await self.get_task(task_id)
        if task:
            await self.repo.delete_task(task_id)

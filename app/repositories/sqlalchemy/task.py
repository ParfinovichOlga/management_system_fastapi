from ..abstract.task import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task, TaskStatus
from sqlalchemy import select, insert, and_
from sqlalchemy.orm import selectinload
from typing import List
from datetime import date, datetime


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task(self, task_id: int) -> Task:
        task = await self.db.scalar(select(Task).where(Task.id == task_id))
        return task

    async def get_task_with_comments(self, task_id: int) -> Task:
        task = await self.db.scalar(
            select(Task).options(selectinload(Task.comments)).where(Task.id == task_id)
        )
        return task

    async def get_tasks(self) -> List[Task]:
        tasks = await self.db.scalars(select(Task))
        return tasks.all()

    async def get_user_tasks(self, user_id: int) -> List[Task]:
        user_tasks = await self.db.scalars(
            select(Task).where(Task.assigned_to == user_id)
        )
        return user_tasks.all()

    async def get_tasks_for_period(self, user_id: int, start: datetime, end: datetime):
        tasks = await self.db.scalars(
            select(Task)
            .where(
                and_(
                    Task.assigned_to == user_id,
                    Task.deadline >= start,
                    Task.deadline < end,
                )
            )
            .order_by(Task.deadline)
        )
        return tasks.all()

    async def create_task(self, description: str, deadline: date):
        await self.db.execute(
            insert(Task).values(description=description, deadline=deadline)
        )
        await self.db.commit()

    async def update_task(
        self,
        task_id: int,
        description: str = None,
        deadline: date = None,
        status: TaskStatus = None,
        assigned_to: int = None,
    ):
        task = await self.get_task(task_id)
        if not task:
            return None
        task.description = description if description else task.description
        task.deadline = deadline if deadline else task.deadline
        task.status = status if status else task.status
        task.assigned_to = assigned_to if assigned_to else task.assigned_to
        await self.db.commit()
        return task

    async def delete_task(self, task_id: int):
        task = await self.get_task(task_id)
        if task:
            await self.db.delete(task)
            await self.db.commit()

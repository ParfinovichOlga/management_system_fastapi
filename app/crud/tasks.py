from ..models import Task, TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from datetime import date
from typing import List


async def get_task(db: AsyncSession, task_id: int) -> Task:
    task = await db.scalar(select(Task).where(Task.id == task_id))
    return task


async def get_task_with_comments(db: AsyncSession, task_id: int) -> Task:
    task = await db.scalar(select(Task).options(
        selectinload(Task.comments)).where(Task.id == task_id))
    return task


async def get_tasks(db: AsyncSession) -> List[Task]:
    tasks = await db.scalars(select(Task))
    return tasks.all()


async def get_user_tasks(db: AsyncSession, user_id: int) -> List[Task]:
    user_tasks = await db.scalars(
        select(Task).where(Task.assigned_to == user_id))
    return user_tasks.all()


async def create_task(db: AsyncSession, description: str, deadline: date):
    await db.execute(insert(Task).values(description=description,
                                         deadline=deadline))
    await db.commit()


async def update_task(db: AsyncSession,
                      task_id: int,
                      description: str = None,
                      deadline: date = None,
                      status: TaskStatus = None,
                      assigned_to: int = None):
    task = await get_task(db, task_id)
    if not task:
        return None
    task.description = description if description else task.description
    task.deadline = deadline if deadline else task.deadline
    task.status = status if status else task.status
    task.assigned_to = assigned_to if assigned_to else task.assigned_to
    await db.commit()
    return task


async def delete_task(db: AsyncSession, task_id: int):
    task = await get_task(db, task_id)
    if task:
        await db.delete(task)
        await db.commit()

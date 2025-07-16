from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.routers.auth import get_current_user_strict
from ..schemas import CreateTask
from app.models import Task


router = APIRouter(
    prefix='/task',
    tags=['task']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_task(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        created_task: CreateTask):
    if not user or user['role'] != 'manager':
        raise  HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    await db.execute(insert(Task).values(description=created_task.description,
                                   deadline=created_task.deadline))
    await db.commit()
    
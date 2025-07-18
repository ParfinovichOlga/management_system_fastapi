from fastapi import (
    APIRouter, Depends,
    Path, HTTPException
)
from starlette import status
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user_strict
from ..schemas import CreateTask, UpdateTask
from app.models import TaskStatus, Roles
from app.crud import tasks, users


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    await tasks.create_task(db=db, description=created_task.description,
                            deadline=created_task.deadline)


@router.get('/tasks', status_code=status.HTTP_200_OK)
async def read_all_tasks(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    return await tasks.get_tasks(db)


@router.get('/my_tasks', status_code=status.HTTP_200_OK)
async def read_assigned_to_user_tasks(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    user_tasks = await tasks.get_user_tasks(db, user['id'])
    return user_tasks


@router.get('/{task_id}', status_code=status.HTTP_200_OK)
async def task_detail(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        task_id: Annotated[int, Path(gt=0)]):
    task = await tasks.get_task_with_comments(db, task_id)
    if task:
        return task

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Task wasn't found"
    )


@router.put('/take/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def take_task(db: Annotated[AsyncSession, Depends(get_db)],
                    user: Annotated[dict, Depends(get_current_user_strict)],
                    task_id: Annotated[int, Path(gt=0)]):
    task = await tasks.get_task(db, task_id)
    user = await users.get_user(db, user['id'])
    if task and user:
        if task.status != TaskStatus.opened:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You can change the status only for tasks with \
                        the open status '
            )
        await tasks.update_task(db=db, task_id=task_id,
                                status=TaskStatus.in_progress,
                                assigned_to=user.id)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task wasn't found"
        )


@router.put('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_task(db: Annotated[AsyncSession, Depends(get_db)],
                      user: Annotated[dict, Depends(get_current_user_strict)],
                      update_request: UpdateTask,
                      task_id: Annotated[int, Path(gt=0)]):
    if user['role'] != Roles.manager.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    if update_request.assigned_to:
        assigned_user = await users.get_user(db, update_request.assigned_to)
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There are no user to assign task'
            )

    curr_task = await tasks.update_task(db, task_id,
                                        update_request.description,
                                        update_request.deadline,
                                        update_request.status,
                                        update_request.assigned_to)
    if not curr_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task wasn't found"
        )


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(db: Annotated[AsyncSession, Depends(get_db)],
                      user: Annotated[dict, Depends(get_current_user_strict)],
                      task_id: Annotated[int, Path(gt=0)]):
    if not user or user['role'] != Roles.manager.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    task_to_delete = await tasks.get_task(db=db, task_id=task_id)
    if not task_to_delete:
        raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail='Task not found.'
             )
    await tasks.delete_task(db, task_id)

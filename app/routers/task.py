from fastapi import APIRouter, Depends, Path, HTTPException
from app.dependencies import get_task_repository, get_user_repository
from app.repositories.abstract.task import TaskRepository
from app.repositories.abstract.user import UserRepository
from starlette import status
from typing import Annotated
from app.routers.auth import get_current_user_strict
from ..schemas import CreateTask, UpdateTask
from app.models import TaskStatus, Roles
from app.services import tasks, users


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    created_task: CreateTask,
):
    task_service = tasks.TaskService(repo)
    if not user or user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    await task_service.create_task(
        description=created_task.description, deadline=created_task.deadline
    )


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def read_all_tasks(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    task_service = tasks.TaskService(repo)
    return await task_service.get_tasks()


@router.get("/my_tasks", status_code=status.HTTP_200_OK)
async def read_assigned_to_user_tasks(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    task_service = tasks.TaskService(repo)
    return await task_service.get_user_tasks(user["id"])


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def task_detail(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    task_id: Annotated[int, Path(gt=0)],
):
    task_service = tasks.TaskService(repo)
    task = await task_service.get_task_with_comments(task_id)
    if task:
        return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Task wasn't found"
    )


@router.put("/take/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def take_task(
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    task_id: Annotated[int, Path(gt=0)],
):
    task_service = tasks.TaskService(task_repo)
    user_service = users.UserService(user_repo)
    task = await task_service.get_task(task_id)
    user = await user_service.get_user(user["id"])
    if task and user:
        if task.status != TaskStatus.opened:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only for tasks with open status ",
            )
        await task_service.update_task(
            task_id=task_id, status=TaskStatus.in_progress, assigned_to=user.id
        )

    elif not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task wasn't found"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User wasn't found"
        )


@router.put("/done/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_done(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    task_id: Annotated[int, Path(gt=0)],
):
    task_service = tasks.TaskService(repo)
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task wasn't found"
        )
    if task.assigned_to != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assigned user can complite task",
        )
    await task_service.update_task(task_id=task_id, status="done")


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    update_request: UpdateTask,
    task_id: Annotated[int, Path(gt=0)],
):
    task_service = tasks.TaskService(task_repo)
    user_service = users.UserService(user_repo)
    if user["role"] != Roles.manager.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    if update_request.assigned_to:
        assigned_user = await user_service.get_user(update_request.assigned_to)
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There are no user to assign task",
            )

    curr_task = await task_service.update_task(
        task_id,
        update_request.description,
        update_request.deadline,
        update_request.status,
        update_request.assigned_to,
    )
    if not curr_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task wasn't found"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    task_id: Annotated[int, Path(gt=0)],
):
    task_service = tasks.TaskService(repo)
    if not user or user["role"] != Roles.manager.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    task_to_delete = await task_service.get_task(task_id=task_id)
    if not task_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found."
        )
    await task_service.delete_task(task_id)

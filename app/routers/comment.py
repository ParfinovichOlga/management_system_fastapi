from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from app.dependencies import get_comment_repository, get_task_repository
from app.repositories.abstract.comment import CommentRepository
from app.repositories.abstract.task import TaskRepository
from .auth import get_current_user_strict
from ..services import tasks, comments
from ..schemas import RequestedComment
from typing import Annotated


router = APIRouter(prefix="/comment", tags=["comment"])


@router.post("/{task_id}", status_code=status.HTTP_201_CREATED)
async def add_commenet(
    repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    task_id: Annotated[int, Path(gt=0)],
    comment: RequestedComment,
):
    comment_service = comments.CommentService(repo)
    task_service = tasks.TaskService(task_repo)
    commented_task = await task_service.get_task(task_id)
    if not commented_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no task found"
        )
    await comment_service.create_comment(
        text=comment.text, user_id=user["id"], task_id=commented_task.id
    )


@router.put("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
    repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    comment_id: Annotated[int, Path(gt=0)],
    update_comment: RequestedComment,
):
    comment_service = comments.CommentService(repo)
    comment = await comment_service.get_comment_with_author(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no comment found"
        )
    if comment.author.id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    await comment_service.update_comment(comment_id, update_comment.text)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    comment_id: Annotated[int, Path(gt=0)],
):
    comment_service = comments.CommentService(repo)
    comment = await comment_service.get_comment_with_author(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no comment found"
        )
    if comment.author.id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    await comment_service.delete_comment(comment_id)

from fastapi import (
    APIRouter, Depends,
    Path, HTTPException
)
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from ..backend.db_depends import get_db
from .auth import get_current_user_strict
from ..crud import tasks, comments
from ..schemas import RequestedComment
from typing import Annotated


router = APIRouter(
    prefix='/comment',
    tags=['comment']
)


@router.post('/{task_id}', status_code=status.HTTP_201_CREATED)
async def add_commenet(db: Annotated[AsyncSession, Depends(get_db)],
                       user: Annotated[dict, Depends(get_current_user_strict)],
                       task_id: Annotated[int, Path(gt=0)],
                       comment: RequestedComment):
    commented_task = await tasks.get_task(db, task_id)
    if not commented_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no task found'
        )
    await comments.create_comment(
        db=db, text=comment.text,
        user_id=user['id'], task_id=commented_task.id
        )


@router.put('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        comment_id: Annotated[int, Path(gt=0)],
        update_comment: RequestedComment):
    comment = await comments.get_comment_with_author(db, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no comment found'
        )
    if comment.author.id != user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    await comments.update_commit(db, comment_id, update_comment.text)


@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        comment_id: Annotated[int, Path(gt=0)]):
    comment = await comments.get_comment_with_author(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no comment found'
        )
    if comment.author.id != user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    await comments.delete_comment(db, comment_id)

from ..models import Comment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload
from datetime import datetime


async def get_comment(db: AsyncSession, id: int):
    comment = await db.scalar(select(Comment).where(Comment.id == id))
    return comment


async def get_comment_with_author(db: AsyncSession, id: int):
    comment = await db.scalar(
        select(Comment).options(
            joinedload(Comment.author)).where(Comment.id == id))
    return comment


async def create_comment(db: AsyncSession,
                         task_id: int, user_id: int,
                         text: str
                         ):
    await db.execute(insert(Comment).values(
        text=text,
        user_id=user_id,
        task_id=task_id
    ))
    await db.commit()


async def update_commit(db: AsyncSession, id: int, text: str):
    comment = await get_comment(db, id)
    if comment:
        comment.text = text
        comment.date = datetime.now()
        await db.commit()


async def delete_comment(db: AsyncSession, id: int):
    comment = await get_comment(db, id)
    if comment:
        await db.delete(comment)
        await db.commit()

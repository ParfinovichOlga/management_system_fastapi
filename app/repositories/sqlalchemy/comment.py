from ..abstract.comment import CommentRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload
from app.models import Comment
from datetime import datetime


class SQLAlchemyCommentRepository(CommentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_comment(self, id: int):
        comment = await self.db.scalar(select(Comment).where(Comment.id == id))
        return comment

    async def get_comment_with_author(self, id: int):
        comment = await self.db.scalar(
            select(Comment).options(joinedload(Comment.author)).where(Comment.id == id)
        )
        return comment

    async def create_comment(self, task_id: int, user_id: int, text: str):
        await self.db.execute(
            insert(Comment).values(text=text, user_id=user_id, task_id=task_id)
        )
        await self.db.commit()

    async def update_comment(self, id: int, text: str):
        comment = await self.get_comment(id)
        if comment:
            comment.text = text
            comment.date = datetime.now()
            await self.db.commit()

    async def delete_comment(self, id: int):
        comment = await self.get_comment(id)
        if comment:
            await self.db.delete(comment)
            await self.db.commit()

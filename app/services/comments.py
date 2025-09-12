from app.repositories.abstract.comment import CommentRepository


class CommentService:
    def __init__(self, repo: CommentRepository):
        self.repo = repo

    async def get_comment(self, id: int):
        return await self.repo.get_comment(id)

    async def get_comment_with_author(self, id: int):
        return await self.repo.get_comment_with_author(id)

    async def create_comment(self, task_id: int, user_id: int, text: str):
        await self.repo.create_comment(task_id, user_id, text)

    async def update_comment(self, id: int, text: str):
        comment = await self.get_comment(id)
        if comment:
            await self.repo.update_comment(id, text)

    async def delete_comment(self, id: int):
        comment = await self.get_comment(id)
        if comment:
            await self.repo.delete_comment(id)

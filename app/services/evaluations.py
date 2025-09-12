from app.repositories.abstract.evaluation import EvaluationRepository
from datetime import date


class EvaluationService:
    def __init__(self, repo: EvaluationRepository):
        self.repo = repo

    async def create_evaluation(self, task_id: int, user_id: int, grade: int):
        await self.repo.create_evaluation(task_id, user_id, grade)

    async def get_user_evaluations(self, user_id: int, start: date, end: date):
        return await self.repo.get_user_evaluations(user_id, start, end)

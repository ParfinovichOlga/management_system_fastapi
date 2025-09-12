from app.repositories.abstract.evaluation import EvaluationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, func, and_
from sqlalchemy.orm import selectinload
from app.models import Evaluation
from datetime import date


class SQLAlchemyEvaluationRepository(EvaluationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_evaluation(self, task_id: int, user_id: int, grade: int):
        await self.db.execute(
            insert(Evaluation).values(user_id=user_id, task_id=task_id, grade=grade)
        )
        await self.db.commit()

    async def get_user_evaluations(self, user_id: int, start: date, end: date):
        result = await self.db.scalars(
            select(Evaluation)
            .options(selectinload(Evaluation.task))
            .where(
                and_(
                    Evaluation.user_id == user_id,
                    func.date(Evaluation.date) >= start,
                    func.date(Evaluation.date) <= end,
                )
            )
            .order_by("date")
        )
        evaluations = result.all()

        avg_grade = await self.db.scalar(
            select(func.avg(Evaluation.grade)).where(
                and_(
                    Evaluation.user_id == user_id,
                    Evaluation.date >= start,
                    Evaluation.date <= end,
                )
            )
        )
        return (evaluations, round(avg_grade, 1) if avg_grade else 0)

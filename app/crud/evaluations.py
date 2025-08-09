from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy import func, and_
from sqlalchemy.orm import selectinload
from datetime import date
from ..models import Evaluation


async def create_evaluation(
        db: AsyncSession,
        task_id: int,
        user_id: int,
        grade: int):
    await db.execute(
        insert(Evaluation).values(
            user_id=user_id,
            task_id=task_id,
            grade=grade))
    await db.commit()


async def get_user_evaluations(
        db: AsyncSession, user_id: int,
        start: date, end: date):
    result = await db.scalars(
        select(Evaluation)
        .options(selectinload(Evaluation.task))
        .where(
            and_(
                Evaluation.user_id == user_id,
                func.date(Evaluation.date) >= start,
                func.date(Evaluation.date) <= end
                )
        ).order_by('date')
    )
    evaluations = result.all()

    avg_grade = await db.scalar(
        select(func.avg(Evaluation.grade))
        .where(
            and_(
                Evaluation.user_id == user_id,
                func.date(Evaluation.date) >= start,
                func.date(Evaluation.date) <= end
            )
        )
    )

    return evaluations, round(avg_grade, 1) if avg_grade else 0

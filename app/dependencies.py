from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.repositories.sqlalchemy.user import SQLAlchemyUserRepository
from app.repositories.sqlalchemy.team import SQLAlchemyTeamRepository
from app.repositories.sqlalchemy.meeting import SQLAlchemyMeetingRepository
from app.repositories.sqlalchemy.task import SQLAlchemyTaskRepository
from app.repositories.sqlalchemy.comment import SQLAlchemyCommentRepository
from app.repositories.sqlalchemy.evaluation import SQLAlchemyEvaluationRepository


async def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyUserRepository(db)


async def get_team_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyTeamRepository(db)


async def get_meeting_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyMeetingRepository(db)


async def get_task_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyTaskRepository(db)


async def get_comment_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyCommentRepository(db)


async def get_evaluation_repository(db: Annotated[AsyncSession, Depends(get_db)]):
    return SQLAlchemyEvaluationRepository(db)

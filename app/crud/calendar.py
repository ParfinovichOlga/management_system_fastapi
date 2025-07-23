from ..models import Task, Meeting, user_meeting
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from datetime import datetime, timezone


async def get_daily_events(db: AsyncSession, user_id: int):
    today = datetime.now(timezone.utc).date()
    tasks_for_today = await db.scalars(
        select(Task).where(
            and_(
                Task.assigned_to == user_id,
                Task.deadline == today
            )
        )
    )
    todays_meetings = await db.scalars(
        select(Meeting).join(user_meeting).where(
            and_(
                user_meeting.c.user_id == user_id,
                func.date(Meeting.date) == today
            )
        )
    )
    return tasks_for_today.all(), todays_meetings.all()


async def get_monthly_events(db: AsyncSession, user_id: int):
    curr_month = datetime.now(timezone.utc).month
    curr_year = datetime.now().year
    tasks_for_month = await db.scalars(
        select(Task).where(
            and_(
                Task.assigned_to == user_id,
                extract('month', Task.deadline) == curr_month,
                extract('year', Task.deadline) == curr_year
            )
        ).order_by(Task.deadline)
    )

    month_meetings = await db.scalars(
        select(Meeting).join(user_meeting).where(
            and_(
                user_meeting.c.user_id == user_id,
                extract('month', Meeting.date) == curr_month,
                extract('year', Meeting.date) == curr_year
            )
        ).order_by(Meeting.date)
    )

    return tasks_for_month.all(), month_meetings.all()

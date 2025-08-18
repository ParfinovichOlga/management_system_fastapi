from ..models import Task, Meeting, user_meeting
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta


async def get_daily_events(db: AsyncSession, user_id: int):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    tasks_for_today = await db.scalars(
        select(Task).where(
            and_(
                Task.assigned_to == user_id,
                Task.deadline >= start,
                Task.deadline < end
            )
        )
    )
    todays_meetings = await db.scalars(
        select(Meeting).join(user_meeting).where(
            and_(
                user_meeting.c.user_id == user_id,
                Meeting.date >= start,
                Meeting.date < end
            )
        )
    )
    return tasks_for_today.all(), todays_meetings.all()


async def get_monthly_events(db: AsyncSession, user_id: int):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    if now.month == 12:
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    tasks_for_month = await db.scalars(
        select(Task).where(
            and_(
                Task.assigned_to == user_id,
                Task.deadline >= start,
                Task.deadline < end
            )
        ).order_by(Task.deadline)
    )

    month_meetings = await db.scalars(
        select(Meeting).join(user_meeting).where(
            and_(
                user_meeting.c.user_id == user_id,
                Meeting.date >= start,
                Meeting.date < end
            )
        ).order_by(Meeting.date)
    )

    return tasks_for_month.all(), month_meetings.all()

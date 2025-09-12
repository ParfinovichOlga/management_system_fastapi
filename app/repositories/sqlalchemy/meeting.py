from ..abstract.meeting import MeetingRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models import Meeting, user_meeting
from datetime import datetime, timedelta


class SQLAlchemyMeetingRepository(MeetingRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_meeting(self, meeting: dict):
        new_meeting = Meeting(**meeting)
        self.db.add(new_meeting)
        await self.db.commit()

    async def get_meeting(self, meeting_id: int):
        meeting = await self.db.scalar(select(Meeting).where(Meeting.id == meeting_id))
        return meeting

    async def get_user_meetings(self, user_id: int):
        meetings = await self.db.scalars(
            select(Meeting)
            .join(user_meeting)
            .where(
                and_(
                    user_meeting.c.user_id == user_id,
                    Meeting.date >= datetime.now().date(),
                )
            )
            .options(selectinload(Meeting.participants))
        )
        return meetings.all()

    async def get_meetings_for_period(self, user_id, start, end):
        meetings = await self.db.scalars(
            select(Meeting)
            .join(user_meeting)
            .where(
                and_(
                    user_meeting.c.user_id == user_id,
                    Meeting.date >= start,
                    Meeting.date < end,
                )
            )
            .order_by(Meeting.date)
        )
        return meetings.all()

    async def have_meeting(self, user_id: int, date: datetime):
        delta = timedelta(seconds=3600)
        meetings = await self.db.scalars(
            select(Meeting)
            .join(user_meeting)
            .where(
                and_(
                    user_meeting.c.user_id == user_id,
                    Meeting.date >= date - delta,
                    Meeting.date <= date + delta,
                )
            )
        )
        return meetings.first()

    async def delete_meeting(self, meeting_id: int):
        deleted_meeting = await self.get_meeting(meeting_id)
        if deleted_meeting:
            await self.db.delete(deleted_meeting)
            await self.db.commit()

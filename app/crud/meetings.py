from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..models import Meeting
from .users import get_user
from typing import List
from sqlalchemy import select
from datetime import datetime


async def add_meeting(
        db: AsyncSession,
        user_id: int,
        title: str,
        description: str,
        date: datetime,
        participants: List[int]):
    users = [await get_user(db, user_id)]
    for id in participants:
        participant = await get_user(db, id)
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There's no user with {id} id"
            )
        if participant not in users:
            users.append(participant)
    new_meeting = Meeting(
        user_id=user_id,
        date=date,
        title=title,
        description=description,
        participants=users
    )
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)


async def get_meeting(db: AsyncSession, meeting_id: int):
    meeting = await db.scalar(select(Meeting).where(Meeting.id == meeting_id))
    return meeting


async def delete_meeting(db: AsyncSession, meeting_id: int):
    deleted_meeting = await get_meeting(db, meeting_id)
    if deleted_meeting:
        await db.delete(deleted_meeting)
        await db.commit()

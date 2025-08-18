from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from pydantic import TypeAdapter
from ..backend.db_depends import get_db
from ..crud import calendar
from .auth import get_current_user_strict
from ..schemas import MeetingOut


router = APIRouter(
    prefix='/calendar',
    tags=['calendar']
)


@router.get('/today', status_code=status.HTTP_200_OK)
async def get_events_for_today(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    tasks, meetings = await calendar.get_daily_events(
        db, user['id']
    )
    adapter = TypeAdapter(list[MeetingOut])
    meetings = adapter.validate_python(meetings, from_attributes=True)

    return {'tasks': tasks, 'meetings': meetings}


@router.get('/month', status_code=status.HTTP_200_OK)
async def get_events_for_month(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    tasks, meetings = await calendar.get_monthly_events(
        db, user['id']
    )
    adapter = TypeAdapter(list[MeetingOut])
    meetings = adapter.validate_python(meetings, from_attributes=True)
    return {'tasks': tasks, 'meetings': meetings}

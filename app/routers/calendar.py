from fastapi import APIRouter, status, Depends
from typing import Annotated
from pydantic import TypeAdapter
from app.dependencies import get_task_repository, get_meeting_repository
from app.repositories.abstract.task import TaskRepository
from app.repositories.abstract.meeting import MeetingRepository
from ..services import calendar
from .auth import get_current_user_strict
from ..schemas import MeetingOut


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/today", status_code=status.HTTP_200_OK)
async def get_events_for_today(
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    meeting_repo: Annotated[MeetingRepository, Depends(get_meeting_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    calendar_service = calendar.CalendarService(task_repo, meeting_repo)
    tasks, meetings = await calendar_service.get_daily_events(user["id"])
    adapter = TypeAdapter(list[MeetingOut])
    meetings = adapter.validate_python(meetings, from_attributes=True)

    return {"tasks": tasks, "meetings": meetings}


@router.get("/month", status_code=status.HTTP_200_OK)
async def get_events_for_month(
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    meeting_repo: Annotated[MeetingRepository, Depends(get_meeting_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    calendar_service = calendar.CalendarService(task_repo, meeting_repo)
    tasks, meetings = await calendar_service.get_monthly_events(user["id"])
    adapter = TypeAdapter(list[MeetingOut])
    meetings = adapter.validate_python(meetings, from_attributes=True)
    return {"tasks": tasks, "meetings": meetings}

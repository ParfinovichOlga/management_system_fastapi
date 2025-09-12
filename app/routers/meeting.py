from fastapi import APIRouter, Depends, Path, HTTPException, status
from .auth import get_current_user_strict
from ..schemas import CreateMeeting, MeetingOut
from ..services import meetings
from app.dependencies import get_meeting_repository, get_user_repository
from app.repositories.abstract.meeting import MeetingRepository
from app.repositories.abstract.user import UserRepository
from typing import Annotated


router = APIRouter(prefix="/meeting", tags=["meeting"])


@router.get("/my_meetings", status_code=status.HTTP_200_OK)
async def get_my_meetings(
    repo: Annotated[MeetingRepository, Depends(get_meeting_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    meeting_service = meetings.MeetingService(repo)
    curr_user_meetings = await meeting_service.get_user_meetings(user["id"])
    return [MeetingOut.model_validate(m) for m in curr_user_meetings]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    repo: Annotated[MeetingRepository, Depends(get_meeting_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    created_meeting: CreateMeeting,
):
    meeting_service = meetings.MeetingService(repo)
    await meeting_service.add_meeting(created_meeting, user_repo, user["id"])


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_meeting(
    repo: Annotated[MeetingRepository, Depends(get_meeting_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    meeting_id: Annotated[int, Path(gt=0)],
):
    meeting_service = meetings.MeetingService(repo)
    canceled_meeting = await meeting_service.get_meeting(meeting_id)
    if not canceled_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found"
        )
    if canceled_meeting.user_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only initiator can cancel meeting",
        )
    await meeting_service.delete_meeting(meeting_id)

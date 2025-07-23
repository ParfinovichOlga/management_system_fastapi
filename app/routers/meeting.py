from fastapi import APIRouter, Depends, Path, HTTPException, status
from ..backend.db_depends import get_db
from .auth import get_current_user_strict
from ..schemas import CreateMeeting
from ..crud import meetings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


router = APIRouter(
    prefix='/meeting',
    tags=['meeting']
)


@router.get('/my_meetings', status_code=status.HTTP_200_OK)
async def get_my_meetings(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    curr_user_meetings = await meetings.get_user_meetings(db, user['id'])
    return curr_user_meetings


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_meeting(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        created_meeting: CreateMeeting):
    another_meeting = await meetings.have_meeting(
        db, user['id'], created_meeting.date
    )
    if another_meeting is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have another meeting at {another_meeting.date}"
        )
    await meetings.add_meeting(
        db=db, user_id=user['id'],
        title=created_meeting.title,
        description=created_meeting.description,
        date=created_meeting.date,
        participants=created_meeting.participants)


@router.delete('/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_meeting(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        meeting_id: Annotated[int, Path(gt=0)]):
    canceled_meeting = await meetings.get_meeting(db, meeting_id)
    if canceled_meeting.user_id != user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only initiator can cancel meeting'
        )
    await meetings.delete_meeting(db, meeting_id)

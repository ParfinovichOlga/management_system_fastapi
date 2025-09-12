from fastapi import HTTPException, status
from .users import UserService
from typing import List
from datetime import datetime
from app.repositories.abstract.meeting import MeetingRepository
from app.repositories.abstract.user import UserRepository
from app.schemas import CreateMeeting


class MeetingService:
    def __init__(self, repo: MeetingRepository):
        self.repo = repo

    async def add_meeting(
        self, meeting: CreateMeeting, user_repo: UserRepository, user_id
    ):
        user_service = UserService(user_repo)
        users = []
        if user_id not in meeting.participants:
            meeting.participants.append(user_id)
        for id in meeting.participants:
            participant = await user_service.get_user(id)
            if participant is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"There's no user with {id} id",
                )

            overlap_meeting = await self.have_meeting(id, meeting.date)
            if overlap_meeting is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{participant.name} have meeting {overlap_meeting.date}",
                )
            if participant not in users:
                users.append(participant)

        meeting = meeting.model_dump()
        meeting["participants"] = users
        meeting["user_id"] = user_id
        await self.repo.add_meeting(meeting)

    async def get_meeting(self, meeting_id: int):
        return await self.repo.get_meeting(meeting_id)

    async def get_user_meetings(self, user_id: int):
        return await self.repo.get_user_meetings(user_id)

    async def have_meeting(self, user_ids: List[int], date: datetime):
        return await self.repo.have_meeting(user_ids, date)

    async def delete_meeting(self, meeting_id: int):
        await self.repo.delete_meeting(meeting_id)

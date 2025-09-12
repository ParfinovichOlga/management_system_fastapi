from abc import ABC, abstractmethod
from app.schemas import CreateMeeting, MeetingOut
from typing import List, Optional
from datetime import datetime


class MeetingRepository(ABC):
    """
    Defines the interface all MeetingRepository implementations must follow.
    """

    @abstractmethod
    async def add_meeting(self, meeting: CreateMeeting) -> None:
        pass

    @abstractmethod
    async def get_meeting(meeting_id: int) -> MeetingOut:
        pass

    @abstractmethod
    async def get_user_meetings(self, user_id: int) -> List[MeetingOut]:
        pass

    @abstractmethod
    async def get_meetings_for_period(
        self, user_id: int, start: datetime, end: datetime
    ) -> List[MeetingOut]:
        pass

    @abstractmethod
    async def have_meeting(self, user_id, date: datetime) -> Optional[MeetingOut]:
        pass

    @abstractmethod
    async def delete_meeting(self, meeting_id: int):
        pass

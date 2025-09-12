from ..models import Task, Meeting
from app.repositories.abstract.task import TaskRepository
from app.repositories.abstract.meeting import MeetingRepository
from app.utils import date_processing
from typing import List, Tuple


class CalendarService:
    def __init__(self, task_repo: TaskRepository, meeting_repo: MeetingRepository):
        self.task_repo = task_repo
        self.meeting_repo = meeting_repo

    async def get_daily_events(self, user_id: int) -> Tuple[List[Task], List[Meeting]]:
        start, end = await date_processing.get_today_date()
        tasks_for_today = await self.task_repo.get_tasks_for_period(user_id, start, end)
        todays_meetings = await self.meeting_repo.get_meetings_for_period(
            user_id, start, end
        )
        return tasks_for_today, todays_meetings

    async def get_monthly_events(
        self, user_id: int
    ) -> Tuple[List[Task], List[Meeting]]:
        start, end = await date_processing.get_month_date()
        month_tasks = await self.task_repo.get_tasks_for_period(user_id, start, end)
        month_meetings = await self.meeting_repo.get_meetings_for_period(
            user_id, start, end
        )
        return month_tasks, month_meetings

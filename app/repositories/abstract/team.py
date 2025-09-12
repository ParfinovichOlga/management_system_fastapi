from abc import ABC, abstractmethod
from app.schemas import TeamOut
from app.models import Team
from typing import List


class TeamRepository(ABC):
    """
    Defines the interface all TeamRepository implementations must follow.
    """

    @abstractmethod
    async def get_team(self, id: int) -> Team:
        pass

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Team:
        pass

    @abstractmethod
    async def create_team(self, name: str) -> None:
        pass

    @abstractmethod
    async def get_teams(self) -> List[Team]:
        pass

    @abstractmethod
    async def get_team_with_members(self) -> List[TeamOut]:
        pass

    @abstractmethod
    async def add_members(self, team_id: int, members: List[int]) -> None:
        pass

    @abstractmethod
    async def delete_team(self, team_id: int):
        pass

    @abstractmethod
    async def check_has_manager(self, team_id: int) -> bool:
        pass

    @abstractmethod
    async def update_team_name(self, team_id: int, name: str) -> None:
        pass

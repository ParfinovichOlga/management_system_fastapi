from app.repositories.abstract.team import TeamRepository
from app.repositories.abstract.user import UserRepository
from typing import List
from .users import UserService
from fastapi import HTTPException, status


class TeamService:
    def __init__(self, repo: TeamRepository):
        self.repo = repo

    async def get_team(self, team_id: int):
        return await self.repo.get_team(team_id)

    async def get_team_by_name(self, name: str):
        return await self.repo.get_team_by_name(name)

    async def create_team(self, name: str):
        await self.repo.create_team(name)

    async def get_teams(self):
        return await self.repo.get_teams()

    async def get_team_with_members(self, team_id: int):
        return await self.repo.get_team_with_members(team_id)

    async def add_members(
        self, team_id: int, members: List[int], user_repo: UserRepository
    ):
        user_service = UserService(user_repo)
        members = await user_service.check_users_list(members)
        await self.repo.add_members(team_id, members)

    async def delete_team(self, team_id: int):
        await self.repo.delete_team(team_id)

    async def check_has_manager(self, team_id):
        return await self.repo.check_has_manager(team_id)

    async def update_team_name(self, team_id, name):
        team = await self.repo.get_team(team_id)
        if team:
            team_with_the_same_name = await self.get_team_by_name(name)
            if team_with_the_same_name is None:
                await self.repo.update_team_name(team_id, name)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team with this name already exists",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )

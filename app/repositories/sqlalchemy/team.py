from ..abstract.team import TeamRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from app.models import Team
from typing import List
from collections import Counter


class SQLAlchemyTeamRepository(TeamRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_team(self, team_id: int):
        team = await self.db.scalar(select(Team).where(Team.id == team_id))
        return team

    async def get_team_by_name(self, name: str):
        team = await self.db.scalar(select(Team).where(Team.name == name))
        return team

    async def create_team(self, name: str):
        await self.db.execute(insert(Team).values(name=name))
        await self.db.commit()

    async def get_teams(self):
        teams = await self.db.scalars(select(Team))
        return teams.all()

    async def get_team_with_members(self, team_id: int):
        team = await self.db.scalar(
            select(Team).options(selectinload(Team.members)).where(Team.id == team_id)
        )
        return team

    async def add_members(self, team_id: int, members: List[int]):
        team = await self.get_team_with_members(team_id)
        if team:
            team.members.clear()
            team.members.extend(members)
            await self.db.commit()

    async def delete_team(self, team_id: int):
        team = await self.get_team(team_id)
        if team:
            await self.db.delete(team)
            await self.db.commit()

    async def check_has_manager(self, team_id) -> bool:
        team = await self.get_team_with_members(team_id)
        if team:
            d = Counter([member.role for member in team.members])
            return True if d["manager"] >= 1 else False

    async def update_team_name(self, team_id, name):
        team = await self.get_team(team_id)
        if team:
            team.name = name
            await self.db.commit()

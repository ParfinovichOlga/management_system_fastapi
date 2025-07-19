from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from collections import Counter
from ..models import Team
from ..schemas import TeamOut
from .users import get_user
from typing import List


async def get_team(db: AsyncSession, team_id: int):
    team = await db.scalar(
        select(Team).where(Team.id == team_id))
    return team


async def create_team(db: AsyncSession, name: str):
    await db.execute(insert(Team).values(name=name))
    await db.commit()


async def get_teams(db: AsyncSession):
    teams = await db.scalars(select(Team))
    return teams.all()


async def get_team_with_members(db: AsyncSession, team_id: int):
    team = await db.scalar(
        select(Team).options(selectinload(Team.members)).where(
            Team.id == team_id
        ))
    return TeamOut.model_validate(team) if team else None


async def add_members(db: AsyncSession, team_id: int, members: List[int]):
    team = await get_team_with_members(db, team_id)
    if team:
        team.members = []
        has_manager = False
        for id in members:
            member = await get_user(db, id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'User with {id} id not found'
                )
            elif member.team_id and member.team_id != team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'User with {id} is already in {member.team} team'
                )
            elif member.role == 'manager':
                if has_manager:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='You try to add 2 managers at the team'
                    )
                has_manager = True
            else:
                team.members.append(member)
        await db.commit()


async def delete_team(db: AsyncSession, team_id: int):
    team = await get_team(db, team_id)
    if team:
        await db.delete(team)
        await db.commit()


async def check_has_manager(db: AsyncSession, team_id):
    team = await get_team_with_members(db, team_id)
    if team:
        d = Counter([member.role for member in team.members])
        return True if d['manager'] >= 1 else False

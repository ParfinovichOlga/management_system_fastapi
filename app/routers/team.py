from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ..backend.db_depends import get_db
from ..routers.auth import get_current_user_strict
from ..schemas import CreateTeam, UsersToAdd
from ..crud import teams, users


router = APIRouter(
    prefix='/team',
    tags=['team']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_team(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        created_team: CreateTeam):
    if not user['role'] == 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    await teams.create_team(db, created_team.name)


@router.get('/teams', status_code=status.HTTP_200_OK)
async def get_all_teams(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):
    if not user['role'] == 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    return await teams.get_teams(db)


@router.get('/{team_id}', status_code=status.HTTP_200_OK)
async def get_team_detail(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        team_id: Annotated[int, Path(gt=0)]):
    if user['role'] == 'admin':
        team = await teams.get_team_with_members(db, team_id)
        return team
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )


@router.get('/my_team', status_code=status.HTTP_200_OK)
async def get_user_team(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)]):

    user_model = await users.get_user(db, user['id'])
    if user_model:
        return await teams.get_team_with_members(db, user_model.team_id)


@router.put('/{team_id}', status_code=status.HTTP_204_NO_CONTENT)
async def add_memebers_to_team(
            db: Annotated[AsyncSession, Depends(get_db)],
            user: Annotated[dict, Depends(get_current_user_strict)],
            memebers: UsersToAdd,
            team_id: Annotated[int, Path(gt=0)]
):
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    team = await teams.get_team(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Team not found'
        )
    await teams.add_members(db, team_id, memebers.user_ids)


@router.delete('/{team_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(db: Annotated[AsyncSession, Depends(get_db)],
                      user: Annotated[dict, Depends(get_current_user_strict)],
                      team_id: Annotated[int, Path(gt=0)]):
    if not user or user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    team_to_delete = await teams.get_team(db, team_id)
    if not team_to_delete:
        raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail='Team not found.'
             )
    await teams.delete_team(db, team_id)

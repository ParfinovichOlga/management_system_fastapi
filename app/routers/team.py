from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from typing import Annotated
from app.dependencies import get_team_repository, get_user_repository
from app.repositories.abstract.team import TeamRepository
from app.repositories.abstract.user import UserRepository
from ..routers.auth import get_current_user_strict
from ..schemas import CreateTeam, UsersToAdd, TeamOut
from ..services import teams, users


router = APIRouter(prefix="/team", tags=["team"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_team(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    created_team: CreateTeam,
):
    team_service = teams.TeamService(repo)
    if not user["role"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    team = await team_service.get_team_by_name(created_team.name)
    if team is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists",
        )
    await team_service.create_team(created_team.name)


@router.get("/teams", status_code=status.HTTP_200_OK)
async def get_all_teams(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    team_service = teams.TeamService(repo)
    if not user["role"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return await team_service.get_teams()


@router.get("/my_team", status_code=status.HTTP_200_OK)
async def get_user_team(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
):
    team_service = teams.TeamService(repo)
    user_service = users.UserService(user_repo)
    user_model = await user_service.get_user(user["id"])
    if user_model:
        team = await team_service.get_team_with_members(user_model.team_id)
        return TeamOut.model_validate(team) if team else None


@router.get("/{team_id}", status_code=status.HTTP_200_OK)
async def get_team_detail(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    team_id: Annotated[int, Path(gt=0)],
):
    team_service = teams.TeamService(repo)
    if user["role"] == "admin":
        team = await team_service.get_team_with_members(team_id)
        return TeamOut.model_validate(team) if team else None
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )


@router.put("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_memebers_to_team(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    memebers: UsersToAdd,
    team_id: Annotated[int, Path(gt=0)],
):
    team_service = teams.TeamService(repo)
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    team = await team_service.get_team_with_members(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    await team_service.add_members(team_id, memebers.user_ids, user_repo)


@router.put("/{team_id}/change_name", status_code=status.HTTP_204_NO_CONTENT)
async def update_team_name(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    team_id: Annotated[int, Path(gt=0)],
    update_team: CreateTeam,
):
    team_service = teams.TeamService(repo)
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    await team_service.update_team_name(team_id, update_team.name)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    team_id: Annotated[int, Path(gt=0)],
):
    team_service = teams.TeamService(repo)
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    team_to_delete = await team_service.get_team(team_id)
    if not team_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found."
        )
    await team_service.delete_team(team_id)

from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from app.dependencies import get_user_repository, get_team_repository
from app.repositories.abstract.user import UserRepository
from app.repositories.abstract.team import TeamRepository
from typing import Annotated
from .auth import get_current_user_strict, get_current_user_optional, bcrypt_context
from ..schemas import CreateUser, UserVerification, UserOut
from ..services import users, teams
from ..models import Roles


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
async def read_current_user(
    user: Annotated[dict, Depends(get_current_user_strict)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    service = users.UserService(repo)
    curr_user = await service.get_user(user["id"])
    if curr_user:
        return UserOut.model_validate(curr_user)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user: CreateUser,
    user: Annotated[dict, Depends(get_current_user_optional)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    service = users.UserService(repo)
    if not user:
        existing_user = await service.get_user_by_email(create_user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email is already registered",
            )
        await service.create_user(
            name=create_user.name,
            email=create_user.email,
            password=create_user.password,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You've already registered, registration is not available",
        )


@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    user_verification: UserVerification,
):
    service = users.UserService(repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_model = await service.get_user(user["id"])
    if not bcrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change"
        )
    await service.update_user(id=user["id"], password=user_verification.new_password)


@router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def change_username(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    username: Annotated[str, Path(min_length=2)],
):
    service = users.UserService(repo)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    updated_user = await service.get_user(user["id"])

    if updated_user:
        await service.update_user(id=user["id"], name=username)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )


@router.put("/role/{role}", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_status(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    role: Roles,
    user_id: Annotated[int, Query(gt=0)],
):
    user_service = users.UserService(user_repo)
    team_service = teams.TeamService(team_repo)
    if user["role"] == "admin":
        updated_user = await user_service.get_user(user_id)
        if updated_user:
            if not updated_user.team_id or (
                updated_user.team_id
                and not await team_service.check_has_manager(updated_user.team_id)
            ):
                await user_service.update_user_role(user_id, role.value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You try to add 2 managers at the team",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    user_id: Annotated[int, Path(gt=0)],
):
    service = users.UserService(repo)
    if user["role"] != "admin" or user["id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    user_to_delete = await service.get_user(user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await service.delete_user(user_id)

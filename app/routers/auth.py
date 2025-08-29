from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models import User

from app.backend.db_depends import get_db
from app.backend import redis
from app.schemas import TokenInfo

from datetime import datetime, timedelta, timezone
import jwt
import uuid
from config import config


TOKEN_TYPE = "type"
ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
oauth2_scheme_public = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


router = APIRouter(prefix="/auth", tags=["auth"])


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str
) -> User:
    """Authenticate a user by username and password, return user from database."""
    user = await db.scalar(select(User).where(User.name == username))
    if (
        not user
        or not bcrypt_context.verify(password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def create_access_token(
    username: str, user_id: int, role: str
) -> tuple[str, str]:
    """Create JWT access token and return it with its JTI."""
    payload = {TOKEN_TYPE: ACCESS_TYPE, "sub": username, "id": user_id, "role": role}
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["jti"] = str(uuid.uuid4())
    return (jwt.encode(payload, config.SECRET_KEY, config.ALGORITHM), payload["jti"])


async def create_refresh_token(username: str, user_id: int, role: str, jti: str) -> str:
    """Create JWT refresh token and return it."""
    payload = {TOKEN_TYPE: REFRESH_TYPE, "sub": username, "id": user_id, "role": role}
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    payload["jti"] = jti + "refresh"
    return jwt.encode(payload, config.SECRET_KEY, config.ALGORITHM)


async def extract_user_from_payload(payload: dict) -> dict:
    """Extract user info from JWT payload."""
    return {
        "username": payload.get("sub"),
        "id": payload.get("id"),
        "role": payload.get("role"),
        "jti": payload.get("jti"),
    }


async def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """Return payload from decoded token data."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("jti") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload",
            )
        if await redis.token_in_blacklist(payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This token is invalid or has been revoked",
            )
        if not payload["sub"] or not payload["id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


async def get_current_user_optional(
    token: Annotated[str, Depends(oauth2_scheme_public)],
) -> dict:
    """Return user data from token or None if token is missing."""
    if not token:
        return None
    payload = await get_current_token_payload(token)
    return await extract_user_from_payload(payload)


async def get_current_user_strict(
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> dict:
    """Extract user data from a valid access token."""
    cur_type = payload.get(TOKEN_TYPE)
    if cur_type != ACCESS_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {cur_type} expected {ACCESS_TYPE}",
        )
    return await extract_user_from_payload(payload)


async def get_current_user_for_refresh(
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> dict:
    """Extract user data from a valid refresh token."""
    cur_type = payload.get(TOKEN_TYPE)
    if cur_type != REFRESH_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {cur_type} expected {REFRESH_TYPE}",
        )
    return await extract_user_from_payload(payload)


@router.post("/token", response_model=TokenInfo)
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenInfo:
    """Authenticate user and return access and refresh tokens."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    access_token, token_id = await create_access_token(user.name, user.id, user.role)
    refresh_token = await create_refresh_token(user.name, user.id, user.role, token_id)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenInfo, response_model_exclude_none=True)
async def new_access_token(
    user: Annotated[dict, Depends(get_current_user_for_refresh)],
) -> TokenInfo:
    """Generate a new access token and revoke the old refresh token."""
    token, _ = await create_access_token(
        user["username"],
        user["id"],
        user["role"],
    )
    await redis.add_jti_to_blacklist(user["jti"], config.REFRESH_TOKEN_EXPIRE_MINUTES)
    return TokenInfo(access_token=token)


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(token_deets: Annotated[dict, Depends(get_current_user_strict)]):
    """Revoke access and refresh tokens for the current user."""
    jti = token_deets["jti"]
    await redis.add_jti_to_blacklist(jti, config.ACCESS_TOKEN_EXPIRE_MINUTES)
    await redis.add_jti_to_blacklist(
        jti + "refresh", config.REFRESH_TOKEN_EXPIRE_MINUTES
    )

from fastapi import (
    APIRouter, Depends,
    status, HTTPException
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models import User
from ..schemas import CreateUser
from app.backend.db_depends import get_db

from datetime import datetime, timedelta, timezone
import jwt
from config import SECRET_KEY, ALGORITM

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)],
                            username: str, password: str):
    user = await db.scalar(select(User).where(User.name == username))
    if not user or bcrypt_context.verify(password, user.hashed_password)\
            or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )
    print(user)
    return user


async def create_access_token(
        username: str, user_id: int, role: str, expires_delta: timedelta
        ):
    payload = {
        'sub': username,
        'id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, SECRET_KEY, ALGORITM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM])
        name: str | None = payload.get('sub')
        id: int | None = payload.get('id')
        role: str | None = payload.get('role')
        expire: int | None = payload.get('exp')

        if name is None or id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No access token supplied'
            )
        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid token format'
            )

        curr_time = datetime.now(timezone.utc).timestamp()

        if expire < curr_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired!'
            )

        return {
            'username': name,
            'id': id,
            'role': role
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired'
        )

    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


@router.get('/read_current_user')
async def read_current_user(user: Annotated[dict, Depends(get_current_user)]):
    return {'User': user}


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        create_user: CreateUser):
    await db.execute(insert(User).values(
        name=create_user.name,
        email=create_user.email,
        hashed_password=bcrypt_context.hash(create_user.password),
    ))

    await db.commit()


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(
        user.name, user.id, user.role, expires_delta=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

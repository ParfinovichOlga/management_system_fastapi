from fastapi import (
    APIRouter, Depends, Path, Query,
    status, HTTPException
)
from typing import Annotated, Optional
from .auth import get_current_user_strict, get_current_user_optional, bcrypt_context
from app.backend.db_depends import get_db

from app.models import User
from ..schemas import CreateUser, UserVerification, Roles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/me')
async def read_current_user(db: Annotated[AsyncSession, Depends(get_db)],
                            user: Annotated[dict, Depends(get_current_user_strict)]):    
    return user


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        create_user: CreateUser,
        user: Annotated[dict, Depends(get_current_user_optional)]):
    
    print(user)
    if not user:
        await db.execute(insert(User).values(
            name=create_user.name,
            email=create_user.email,
            hashed_password=bcrypt_context.hash(create_user.password),
        ))

        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You've already registered, registration is not available"
        )

@router.put('/', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: Annotated[AsyncSession, Depends(get_db)],
                          user: Annotated[dict, Depends(get_current_user_strict)],
                          user_verification: UserVerification):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication Failed'
        )
    
    user_model = await db.scalar(select(User).where(User.id==user['id']))
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error on password change'
        )
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    await db.commit()


@router.put('/{username}', status_code=status.HTTP_204_NO_CONTENT)
async def change_username(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        username: Annotated[str, Path(min_length=2)]
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    updated_user = await db.scalar(select(User).where(User.id==user['id']))
    
    if updated_user:
        updated_user.name = username
        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found'
        )
    

@router.put('/role/{role}', status_code=status.HTTP_204_NO_CONTENT)
async def change_user_status(db: Annotated[AsyncSession, Depends(get_db)],
                             user: Annotated[dict, Depends(get_current_user_strict)],
                             role: Roles, user_id: Annotated[int, Query(gt=0)]):
    if user['role'] == 'admin':
        updated_user = await db.scalar(select(User).where(User.id==user_id))    
        if updated_user:
            updated_user.role = role.value
            await db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User not found'
            )
    else:
        raise  HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='You do not have permission to perform this action'
        )        
    
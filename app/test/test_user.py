from fastapi import status
from sqlalchemy import select
import pytest
from ..models import User


@pytest.mark.asyncio
async def test_get_current_user(async_client, test_user):
    response = await async_client.get('user/me')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'email': 'test@example.com',
        'id': 1,
        'is_active': True,
        'name': 'test_user',
        'role': 'staff',
        'team_id': None
    }


@pytest.mark.asyncio
async def test_change_password(async_client, test_user):
    response = await async_client.put(
        'user/', json={'password': 'test123',
                       'new_password': 'test1234578'}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_change_password_invalid_current_password(
        async_client, test_user):
    response = await async_client.put(
        'user/', json={'password': 'test',
                       'new_password': 'test12345'}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


@pytest.mark.asyncio
async def test_change_user_name_success(async_client, test_user, db_session):
    response = await async_client.put('/user/new_test_test')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    user = await db_session.scalar(select(User).where(User.id == 1))
    assert user.name == 'new_test_test'

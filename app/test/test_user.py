from fastapi import status
from sqlalchemy import select, exists
import pytest
from ..models import User
import jwt
from ..routers.auth import SECRET_KEY, ALGORITM
from datetime import timedelta, timezone, datetime


def generate_access_token(user_id: int, username: str, role: str = 'staff'):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": int(expire.timestamp())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITM)


class TestPublicUsers:
    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, async_public_client):
        response = await async_public_client.get('user/me')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_user(self, db_session, async_public_client):
        payload = {
            'email': 'newtestuser@example.com',
            'name': 'test',
            'password': 'pass12345'
        }
        response = await async_public_client.post(
            'user/', json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        created_user = await db_session.scalar(select(User).where(
            User.id == 1
        ))
        assert created_user.email == payload['email']
        assert created_user.name == payload['name']

    @pytest.mark.asyncio
    async def test_create_user_exist(self, async_public_client, test_user):
        payload = {
            'name': 'test_user',
            'password': 'test12345',
            'email': 'test@example.com'
        }
        response = await async_public_client.post('user/', json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'User with this email is already registered'
        }

    @pytest.mark.asyncio
    async def test_create_user_password_to_short(self, async_public_client):
        payload = {
            'email': 'newtestuser@example.com',
            'name': 'test',
            'password': 'pass12'
        }
        response = await async_public_client.post(
            'user/', json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_delete_user(self, async_public_client):
        response = await async_public_client.delete('/user/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthenticatedUser:
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, async_client, test_user):
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
    async def test_get_non_existing_user(self, async_client):
        response = await async_client.get('user/me')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    @pytest.mark.asyncio
    async def test_change_password(self, async_client, test_user):
        response = await async_client.put(
            'user/', json={
                'password': 'test123',
                'new_password': 'test1234578'
                }
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_change_password_invalid_current_password(
            self, async_client, test_user):
        response = await async_client.put(
            'user/', json={
                'password': 'test',
                'new_password': 'test12345'
                }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Error on password change'}

    @pytest.mark.asyncio
    async def test_change_user_name_success(
            self, async_client, test_user, db_session):
        response = await async_client.put('/user/new_test_test')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user = await db_session.scalar(select(User).where(User.id == 1))
        assert user.name == 'new_test_test'

    @pytest.mark.asyncio
    async def test_create_user_by_authenticated_user(
                self, db_session, async_client):
        token = generate_access_token(2, 'test')

        headers = {
            "Authorization": f"Bearer {token}"
        }

        payload = {
            'email': 'newtestuser@example.com',
            'name': 'test',
            'password': 'pass12345'
        }

        response = await async_client.post(
            'user/', json=payload, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail':
            "You've already registered, registration is not available"
        }
        assert await db_session.scalar(select(exists().where(
            User.id == 1
        ))) is False

    @pytest.mark.asyncio
    async def test_delete_user(self, async_client):
        response = await async_client.delete('/user/1')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }

    @pytest.mark.asyncio
    async def test_delete_user_by_manager(self, async_client_manager):
        response = await async_client_manager.delete('/user/1')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }

    @pytest.mark.asyncio
    async def test_change_user_role(
            self, async_client, test_user, db_session):
        response = await async_client.put('user/role/manager?user_id=1')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }
        updated_user = await db_session.scalar(select(User).where(
            User.id == 1
        ))
        assert updated_user.role == 'staff'


class TestAuthenticatedAdminUser:
    @pytest.mark.asyncio
    async def test_delete_user_by_admin(
            self, async_client_admin, db_session, test_user):
        response = await async_client_admin.delete('/user/1')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await db_session.scalar(select(exists().where(
            User.id == 1
        ))) is False

    @pytest.mark.asyncio
    async def test_delete_user_not_exist(
            self, async_client_admin):
        response = await async_client_admin.delete('/user/1')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            'detail': 'User not found'
        }

    @pytest.mark.asyncio
    async def test_change_user_role(
            self, async_client_admin, test_user, db_session):
        response = await async_client_admin.put('user/role/manager?user_id=1')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated_user = await db_session.scalar(select(User).where(
            User.id == 1
        ))
        assert updated_user.role == 'manager'

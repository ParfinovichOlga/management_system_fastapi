from ..routers.auth import (
    authenticate_user,
    create_access_token,
    SECRET_KEY, ALGORITM,
    get_current_user_strict
)
from fastapi import HTTPException, status
import pytest
import jwt
from datetime import timedelta, datetime, timezone


@pytest.mark.asyncio
async def test_authenticate_user(db_session, test_user):
    auth_user = await authenticate_user(db_session, test_user.name, 'test123')
    assert auth_user is not None
    assert auth_user.name == test_user.name

    with pytest.raises(HTTPException) as ex:
        await authenticate_user(db_session, 'wrong user', 'pass123')
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'Invalid authentication credentials'

    with pytest.raises(HTTPException) as ex:
        await authenticate_user(db_session, test_user.name, 'wrongpass')
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'Invalid authentication credentials'


@pytest.mark.asyncio
async def test_create_assess_token():
    name = 'testuser'
    id = 1
    role = 'staff'
    expires_delta = timedelta(days=1)

    token = await create_access_token(name, id, role, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM],
                               options={'verify_signature': False})
    assert decoded_token['sub'] == name
    assert decoded_token['id'] == id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_user_valid_token():
    exp = datetime.now(timezone.utc) + timedelta(minutes=20)
    encode = {
        'sub': 'test_user',
        'id': 1,
        'role': 'staff',
        'exp': exp

    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)
    user = await get_current_user_strict(token)
    assert user == {'username': 'test_user', 'id': 1, 'role': 'staff'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)

    with pytest.raises(HTTPException) as ex:
        await get_current_user_strict(token)
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'Could not validate user'


@pytest.mark.asyncio
async def test_get_current_user_missing_expire_time():
    encode = {
        'sub': 'test_user',
        'id': 1,
        'role': 'staff'
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)

    with pytest.raises(HTTPException) as ex:
        await get_current_user_strict(token)
    assert ex.value.status_code == status.HTTP_400_BAD_REQUEST
    assert ex.value.detail == 'No access token supplied'


@pytest.mark.asyncio
async def test_get_current_user_token_expired():
    exp = datetime.now(timezone.utc) - timedelta(minutes=1)
    encode = {
        'sub': 'test_user',
        'id': 1,
        'role': 'staff',
        'exp': exp

    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)
    with pytest.raises(HTTPException) as ex:
        await get_current_user_strict(token)
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'Token expired!'


@pytest.mark.asyncio
async def test_get_current_user_invalid_expire_format():
    encode = {
        'sub': 'test_user',
        'id': 1,
        'role': 'staff',
        'exp': 'tonight'

    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)
    with pytest.raises(HTTPException) as ex:
        await get_current_user_strict(token)
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'Could not validate user'


@pytest.mark.asyncio
async def test_login_success(test_user, async_client):
    payload = {
        'username': 'test_user',
        'password': 'test123'
    }
    response = await async_client.post(
        '/auth/token',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_user, async_client):
    payload = {
        'username': 'test_user',
        'password': 'wrong_pass'
    }
    response = await async_client.post(
        '/auth/token',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid authentication credentials'}

from ..routers.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    extract_user_from_payload,
    get_current_token_payload,
)
from fastapi import HTTPException, status
import pytest
import jwt
from datetime import timedelta, datetime, timezone
from config import config


async def generate_token(
    type: str, user_id: int = 1, username: str = "test_user", role: str = "staff"
):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "type": type,
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": int(expire.timestamp()),
        "jti": "test_jti_example",
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


@pytest.mark.asyncio
async def test_authenticate_user(db_session, test_user):
    auth_user = await authenticate_user(db_session, test_user.name, "test123")
    assert auth_user is not None
    assert auth_user.name == test_user.name

    with pytest.raises(HTTPException) as ex:
        await authenticate_user(db_session, "wrong user", "pass123")
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == "Invalid authentication credentials"

    with pytest.raises(HTTPException) as ex:
        await authenticate_user(db_session, test_user.name, "wrongpass")
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == "Invalid authentication credentials"


@pytest.mark.asyncio
async def test_create_tokens():
    name = "testuser"
    id = 1
    role = "staff"
    access_exp = int(
        (
            datetime.now(timezone.utc)
            + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        ).timestamp()
    )
    refresh_exp = int(
        (
            datetime.now(timezone.utc)
            + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
        ).timestamp()
    )

    token, jti = await create_access_token(name, id, role)
    decoded_token = jwt.decode(
        token,
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_signature": False},
    )
    assert decoded_token["sub"] == name
    assert decoded_token["id"] == id
    assert decoded_token["role"] == role
    assert decoded_token["type"] == "access"
    assert decoded_token["exp"] == access_exp

    refresh_token = await create_refresh_token(name, id, role, jti)
    decoded_refresh = jwt.decode(
        refresh_token,
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_signature": False},
    )
    assert decoded_refresh["type"] == "refresh"
    assert decoded_refresh["exp"] == refresh_exp


@pytest.mark.asyncio
async def test_get_user_valid_token():
    exp = datetime.now(timezone.utc) + timedelta(minutes=20)
    encode = {
        "type": "accesss",
        "sub": "test_user",
        "id": 1,
        "role": "staff",
        "exp": exp,
        "jti": "test jti indentification",
    }
    token = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    payload = await get_current_token_payload(token)

    user = await extract_user_from_payload(payload)

    assert user == {
        "username": "test_user",
        "id": 1,
        "role": "staff",
        "jti": "test jti indentification",
    }


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "admin"}
    token = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    with pytest.raises(HTTPException) as ex:
        await get_current_token_payload(token)
    assert ex.value.status_code == status.HTTP_400_BAD_REQUEST
    assert ex.value.detail == "Invalid token payload"


@pytest.mark.asyncio
async def test_get_current_user_missing_expire_time():
    encode = {"sub": "test_user", "id": 1, "role": "staff"}
    token = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    with pytest.raises(HTTPException) as ex:
        await get_current_token_payload(token)
    assert ex.value.status_code == status.HTTP_400_BAD_REQUEST
    assert ex.value.detail == "Invalid token payload"


@pytest.mark.asyncio
async def test_get_current_user_token_expired():
    exp = datetime.now(timezone.utc) - timedelta(minutes=1)
    encode = {"sub": "test_user", "id": 1, "role": "staff", "exp": exp}
    token = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    with pytest.raises(HTTPException) as ex:
        await get_current_token_payload(token)
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == "Token expired!"


@pytest.mark.asyncio
async def test_get_current_user_invalid_expire_format():
    encode = {"sub": "test_user", "id": 1, "role": "staff", "exp": "tonight"}
    token = jwt.encode(encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    with pytest.raises(HTTPException) as ex:
        await get_current_token_payload(token)
    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == "Could not validate user"


@pytest.mark.asyncio
async def test_login_success(test_user, async_client):
    payload = {"username": "test_user", "password": "test123"}
    response = await async_client.post(
        "/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_user, async_client):
    payload = {"username": "test_user", "password": "wrong_pass"}
    response = await async_client.post(
        "/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid authentication credentials"}


@pytest.mark.asyncio
async def test_get_new_access_token_with_refresh_token(async_public_client, mocker):
    mocker.patch("app.backend.redis.token_in_blacklist", return_value=None)
    mocker.patch("app.backend.redis.add_jti_to_blacklist", return_value=None)
    token = await generate_token("refresh")
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_public_client.post("/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" not in response.json()


@pytest.mark.asyncio
async def test_get_new_access_token_with_access_token(async_public_client, mocker):
    mocker.patch("app.backend.redis.token_in_blacklist", return_value=None)
    mocker.patch("app.backend.redis.add_jti_to_blacklist", return_value=None)
    token = await generate_token("access")
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_public_client.post("/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token type access expected refresh"}

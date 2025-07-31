from httpx import AsyncClient, ASGITransport
from app.main import app
from fastapi import status
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_return_health_check(async_client):

    response = await async_client.get('/healthy')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'is_healthy': True}

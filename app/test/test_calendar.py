import pytest
import pytest_asyncio
from datetime import date
from fastapi import status
from ..models import Task, TaskStatus
import time_machine


@pytest_asyncio.fixture(scope='function')
async def test_tasks(db_session, test_user):
    task1 = Task(
        description='Test task 1',
        deadline=date(2025, 8, 31),
        assigned_to=1,
        status=TaskStatus.done
    )
    task2 = Task(
        description='Test task 2',
        deadline=date(2025, 8, 26),
        assigned_to=1,
        status=TaskStatus.in_progress
    )

    task3 = Task(
        description='Test task 3',
        deadline=date(2025, 9, 16),
        assigned_to=1,
        status=TaskStatus.in_progress
    )
    db_session.add(task1)
    db_session.add(task2)
    db_session.add(task3)
    await db_session.commit()
    yield


@time_machine.travel("2025-08-31 09:00:00")
@pytest.mark.asyncio
async def test_get_events_for_today(
        async_client, test_meetings, test_tasks):
    response = await async_client.get('calendar/today')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['tasks']) == 1
    assert response.json()['tasks'][0]['deadline'] == '2025-08-31'
    assert len(response.json()['meetings']) == 1
    assert response.json()['meetings'][0]['date'] == '2025-08-31T14:30:00'


@time_machine.travel("2025-08-31 09:00:00")
@pytest.mark.asyncio
async def test_get_admin_events_for_today(
        async_client_admin, test_meetings, test_tasks):
    response = await async_client_admin.get('calendar/today')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['tasks']) == 0
    assert len(response.json()['meetings']) == 1
    assert response.json()['meetings'][0]['date'] == '2025-08-31T14:30:00'


@time_machine.travel("2025-08-25 09:00:00")
@pytest.mark.asyncio
async def test_get_no_events_for_today(
        async_client, test_meetings, test_tasks):
    response = await async_client.get('calendar/today')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'tasks': [], 'meetings': []}


@time_machine.travel("2025-08-31 09:00:00")
@pytest.mark.asyncio
async def test_get_events_for_today_unauthenticated(
        async_public_client, test_meetings, test_tasks):
    response = await async_public_client.get('calendar/today')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@time_machine.travel("2025-08-01 09:00:00")
@pytest.mark.asyncio
async def test_get_events_for_august(
        async_client, test_meetings, test_tasks):
    response = await async_client.get('calendar/month')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['tasks']) == 2
    assert len(response.json()['meetings']) == 1


@time_machine.travel("2025-09-11 09:00:00")
@pytest.mark.asyncio
async def test_get_events_for_september(
        async_client, test_meetings, test_tasks):
    response = await async_client.get('calendar/month')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['tasks']) == 1
    assert len(response.json()['meetings']) == 1


@time_machine.travel("2025-10-1 09:00:00")
@pytest.mark.asyncio
async def test_get_events_for_october(
        async_client, test_meetings, test_tasks):
    response = await async_client.get('calendar/month')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'tasks': [], 'meetings': []}

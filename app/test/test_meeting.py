import pytest
from fastapi import status
import time_machine
from datetime import datetime, timezone
from ..models import Meeting, user_meeting
from ..schemas import MeetingOut
from sqlalchemy import select, and_, exists
from sqlalchemy.orm import selectinload


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_get_my_meetings(async_client, test_meetings, db_session):
    meets = await db_session.scalars(
        select(Meeting)
        .join(user_meeting)
        .where(and_(user_meeting.c.user_id == 1, Meeting.date >= datetime.now().date()))
        .options(selectinload(Meeting.participants))
    )
    meets_out = [
        MeetingOut.model_validate(m).model_dump(mode="json") for m in meets.all()
    ]
    response = await async_client.get("meeting/my_meetings")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json() == meets_out


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_get_meetings_related_to_user(
    async_client_manager, test_meetings, db_session
):
    manager_meets = await db_session.scalars(
        select(Meeting)
        .join(user_meeting)
        .where(and_(user_meeting.c.user_id == 3, Meeting.date >= datetime.now().date()))
        .options(selectinload(Meeting.participants))
    )
    meets_out = [
        MeetingOut.model_validate(m).model_dump(mode="json")
        for m in manager_meets.all()
    ]
    response = await async_client_manager.get("meeting/my_meetings")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == meets_out


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_get_no_meetings(async_client):
    response = await async_client.get("meeting/my_meetings")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_create_meeting(
    async_client, test_user, test_user2, test_user3, db_session
):
    payload = {
        "title": "New meeting",
        "description": "Description",
        "date": "2025-08-31T15:30:00Z",
        "participants": [2, 3],
    }
    response = await async_client.post("meeting/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    new_meet = await db_session.scalar(
        select(Meeting)
        .where(Meeting.id == 1)
        .options(selectinload(Meeting.participants))
    )
    assert new_meet.title == payload["title"]
    assert new_meet.description == payload["description"]
    date = new_meet.date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    assert date == payload["date"]
    assert len(new_meet.participants) == 3


@pytest.mark.parametrize(
    "date", ["2025-08-31T15:00:00Z", "2025-08-31T14:00:00Z", "2025-08-31T15:29:59Z"]
)
@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_create_overlapping_meeting(
    async_client, date, test_user, test_user2, test_user3, test_meetings, db_session
):
    payload = {
        "title": "New meeting",
        "description": "Description",
        "date": date,
        "participants": [2, 3],
    }
    response = await async_client.post("meeting/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "test_user2 have meeting 2025-08-31 14:30:00"}
    assert (
        await db_session.scalar(
            select(exists().where(Meeting.title == payload["title"]))
        )
        is False
    )


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_create_meeting_earlier_than_now(
    async_client, test_user, test_user2, test_user3, db_session
):
    payload = {
        "title": "New meeting",
        "description": "Description",
        "date": "2025-08-25T09:00:00Z",
        "participants": [2, 3],
    }
    response = await async_client.post("meeting/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@time_machine.travel("2025-08-25 10:00:00")
@pytest.mark.asyncio
async def test_create_unknown_participant(
    async_client, test_user, test_user2, test_user3, db_session
):
    payload = {
        "title": "New meeting",
        "description": "Description",
        "date": "2025-08-26T09:00:00Z",
        "participants": [2, 3, 99],
    }
    response = await async_client.post("meeting/", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "There's no user with 99 id"}
    assert (
        await db_session.scalar(
            select(exists().where(Meeting.title == payload["title"]))
        )
        is False
    )


@pytest.mark.asyncio
async def test_create_meeting_unauthenticated(
    async_public_client, test_user, test_user2, test_user3, test_meetings, db_session
):
    payload = {
        "title": "New meeting",
        "description": "Description",
        "date": "2025-08-25T09:00:00Z",
        "participants": [2, 3],
    }
    response = await async_public_client.post("meeting/", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_meeting(async_client, test_meetings, db_session):
    response = await async_client.delete("meeting/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await db_session.scalar(select(exists().where(Meeting.id == 1))) is False


@pytest.mark.asyncio
async def test_delete_meeting_created_by_another_user(
    async_client_admin, test_meetings
):
    response = await async_client_admin.delete("meeting/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Only initiator can cancel meeting"}


@pytest.mark.asyncio
async def test_delete_meeting_unathenticated(async_public_client, test_meetings):
    response = await async_public_client.delete("meeting/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_meeting_not_exists(async_client, test_meetings):
    response = await async_client.delete("meeting/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Meeting not found"}

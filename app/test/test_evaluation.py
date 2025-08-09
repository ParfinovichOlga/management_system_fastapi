import pytest
from fastapi import status
from sqlalchemy import select
from ..models import Evaluation, Task, User
from datetime import date, datetime
from ..routers.auth import bcrypt_context


class TestManagerEvaluations:
    @pytest.mark.asyncio
    async def test_create_evaluation(
            self, async_client_manager,
            test_done_tasks, db_session):

        payload = {'grade': 5}
        response = await async_client_manager.post(
            '/evaluation/2', json=payload
        )

        assert response.status_code == status.HTTP_201_CREATED
        ev = await db_session.scalar(select(Evaluation).where(
            Evaluation.id == 1
        ))
        assert ev.grade == 5
        assert ev.task_id == 2

    @pytest.mark.asyncio
    async def test_create_evaluation_uncompleted_task(
            self, async_client_manager):
        payload = {'grade': 5}
        response = await async_client_manager.post(
            '/evaluation/1', json=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'Only done task can be evaluated'
        }

    @pytest.mark.asyncio
    async def test_evaluate_task_not_exist(
            self, async_client_manager):
        payload = {'grade': 5}
        response = await async_client_manager.post(
            '/evaluation/99', json=payload
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            'detail': 'Task not found'
        }

    @pytest.mark.asyncio
    async def test_get_evaluations(self, async_client_manager):
        response = await async_client_manager.get(
            '/evaluation/?date_start=2025-08-09&date_end=2025-08-09')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Evaluations': [], 'Avarage evaluation': 0}


class TestStaffEvaluations:
    @pytest.mark.asyncio
    async def test_create_evaluation(
            self, async_client,
            test_done_tasks, db_session):

        payload = {'grade': 5}
        response = await async_client.post(
            '/evaluation/2', json=payload
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'Only manager can evaluate tasks.'
        }

    @pytest.mark.asyncio
    async def test_get_evaluations(
            self, async_client, test_evaluations):
        response = await async_client.get(
            '/evaluation/?date_start=2025-07-01&date_end=2025-08-31')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['Evaluations']) == 2
        assert response.json()['Evaluations'][0]['grade'] == 2
        assert response.json()['Evaluations'][1]['grade'] == 5
        assert response.json()['Avarage evaluation'] == 3.5

    @pytest.mark.asyncio
    async def test_get_evaluations_invalid_time_period(
            self, async_client, test_evaluations):
        response = await async_client.get(
            '/evaluation/?date_start=2025-09-01&date_end=2025-08-31')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'The end date must be later than the start date'
        }

    @pytest.mark.asyncio
    async def test_get_evaluations_related_to_user(
            self, async_client_admin, test_evaluations, test_user, db_session):
        other_user = User(
            name='other_user',
            email='otheruser@example.com',
            hashed_password=bcrypt_context.hash('test12345')
        )
        task = Task(
            description='Test task 1',
            deadline=date(2025, 8, 16),
            assigned_to=2,
            status='done'
        )

        await db_session.commit()
        ev = Evaluation(
            grade=5,
            task_id=4,
            user_id=2,
            date=datetime(year=2025, month=8, day=9)
        )
        db_session.add(other_user)
        db_session.add(task)
        db_session.add(ev)
        await db_session.commit()
        response = await async_client_admin.get(
            '/evaluation/?date_start=2025-07-01&date_end=2025-08-31')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['Evaluations']) == 1
        assert response.json()['Evaluations'][0]['grade'] == 5
        assert response.json()['Avarage evaluation'] == 5


class TestUnauthenticatedEvaluations:
    @pytest.mark.asyncio
    async def test_create_evaluation(self, async_public_client):
        payload = {'grade': 5}
        response = await async_public_client.post(
            '/evaluation/2', json=payload
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_evaluations(self, async_public_client):
        response = await async_public_client.get(
            '/evaluation/?date_start=2025-08-09&date_end=2025-08-09')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

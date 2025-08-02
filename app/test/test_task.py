from sqlalchemy import select, exists
from fastapi import status
import pytest
from datetime import date
from ..models import Task, User, TaskStatus


class TestManagerTask:
    """"Tests for task endpoints for managers"""
    @pytest.mark.asyncio
    async def test_read_tasks_authenticated(self, async_client_manager):
        response = await async_client_manager.get('/task/tasks')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'assigned_to': None,
                'description': 'Test task',
                'deadline': '2025-08-16',
                'id': 1,
                'status': 'opened'
            }
        ]

    @pytest.mark.asyncio
    async def test_read_task_detail_authenticated(self, async_client_manager):
        response = await async_client_manager.get('/task/1')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'assigned_to': None,
            'description': 'Test task',
            'deadline': '2025-08-16',
            'id': 1,
            'status': 'opened',
            'comments': []}

    @pytest.mark.asyncio
    async def test_read_unexisting_task(self, async_client_manager):
        response = await async_client_manager.get('/task/9999999')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': "Task wasn't found"}

    @pytest.mark.asyncio
    async def test_create_task(self, db_session, async_client_manager):
        payload = {
            'description': 'New test task',
            'deadline': '2025-08-30'
        }
        response = await async_client_manager.post('/task/', json=payload)
        task = await db_session.scalar(select(Task). where(Task.id == 2))

        assert response.status_code == status.HTTP_201_CREATED
        assert task.description == payload['description']
        assert task.deadline == date.fromisoformat(payload['deadline'])

    @pytest.mark.asyncio
    async def test_update_task(self, db_session, async_client_manager):
        payload = {
            'description': 'Change task',
            'deadline': '2025-08-31',
            'status': 'in progress'
        }
        response = await async_client_manager.put(
            '/task/1', json=payload)
        updated_task = await db_session.scalar(
            select(Task).where(Task.id == 1)
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert updated_task.description == payload['description']
        assert updated_task.deadline == date.fromisoformat(
            payload['deadline']
        )
        assert updated_task.status.value == payload['status']

    @pytest.mark.asyncio
    async def test_update_task_not_found(
            self, db_session, async_client_manager):
        payload = {
            'description': 'Change task',
            'deadline': '2025-08-31',
            'status': 'in progress'
        }
        response = await async_client_manager.put(
            '/task/999', json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_task_with_no_user(
            self, async_client_manager, db_session):
        payload = {
            'description': 'Assign to',
            'deadline': '2025-08-30',
            'assigned_to': 99
        }
        response = await async_client_manager.put(
            '/task/1', json=payload
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            'detail': 'There are no user to assign task'
            }
        task = await db_session.scalar(
            select(Task).where(Task.id == 1)
        )
        assert task.description != payload['description']

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session, async_client_manager):
        response = await async_client_manager.delete('/task/1')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await db_session.scalar(
            select(exists().where(Task.id == 1))) is False

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, async_client_manager):
        response = await async_client_manager.delete('/task/999')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Task not found.'}


class TestStaffTasks:
    """"Tests for task endpoints for staff."""
    @pytest.mark.asyncio
    async def test_create_task_by_staff(self, async_client):
        payload = {
            'description': 'New test task',
            'deadline': '2025-08-30'
        }
        response = await async_client.post('/task/', json=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_task_status_to_in_progress(
            self, async_client, test_user, db_session):
        response = await async_client.put('/task/take/1')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        task = await db_session.scalar(
            select(Task).where(Task.id == 1)
        )
        assert task.status == TaskStatus.in_progress
        assert task.assigned_to == test_user.id

    @pytest.mark.asyncio
    async def test_take_task_not_found(self, async_client, test_user):
        response = await async_client.put('/task/take/9999')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': "Task wasn't found"}

    @pytest.mark.asyncio
    async def test_take_task_no_user(self, async_client):
        response = await async_client.put('/task/take/1')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': "User wasn't found"}

    @pytest.mark.asyncio
    async def test_take_in_progress_status(
            self, async_client, test_user, db_session):
        task2 = Task(
            description='Test task 2',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress
        )
        task3 = Task(
            description='Test task 3',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress,
            assigned_to=1
        )
        task4 = Task(
            description='Test task 4',
            deadline=date(2025, 8, 16),
            status=TaskStatus.done
        )
        db_session.add(task2)
        db_session.add(task3)
        db_session.add(task4)
        await db_session.commit()
        response = await async_client.put('/task/take/2')
        response1 = await async_client.put('/task/take/3')
        response2 = await async_client.put('/task/take/4')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response1.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'Only for tasks with open status '
            }

    @pytest.mark.asyncio
    async def test_mark_task_done(self, async_client, test_user, db_session):
        other_user = User(
            name='other_test_user',
            hashed_password='test123',
            email='test1@example.com'
        )
        db_session.add(other_user)
        await db_session.commit()

        task1 = Task(
            description='Test task 2',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress,
            assigned_to=1
        )
        task2 = Task(
            description='Test task 3',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress,
            assigned_to=2
        )
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()
        response1 = await async_client.put('task/done/2')
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        task = await db_session.scalar(select(Task).where(Task.id == 2))
        assert task.status == TaskStatus.done.value
        response2 = await async_client.put('task/done/3')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.json() == {
            'detail': 'Only assigned user can complite task'
        }

    @pytest.mark.asyncio
    async def test_get_my_tasks(self, db_session, async_client, test_user):
        task = Task(
            description='Test task 2',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress,
            assigned_to=1
        )
        db_session.add(task)
        await db_session.commit()
        response = await async_client.get('task/my_tasks')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 2

    @pytest.mark.asyncio
    async def test_get_all_task_for_staff(self, async_client):
        response = await async_client.get('/task/tasks')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 1

    @pytest.mark.asyncio
    async def test_delete_task_by_staff(self, async_client):
        response = await async_client.delete('task/1')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }


class TestPublicTasks:
    """Testing task endpoints without authorization"""
    @pytest.mark.parametrize('urls', [
        '/task/tasks',
        '/task/my_tasks',
        '/task/1'
    ])
    @pytest.mark.asyncio
    async def test_unauthorized_requests(self, urls, async_public_client):
        response = await async_public_client.get(urls)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_task(self, async_public_client):
        payload = {
            'description': 'New test task',
            'deadline': '2025-08-30'
        }
        response = await async_public_client.post('/task/', json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_task_status_to_in_progress(
            self, async_public_client):
        response = await async_public_client.put('/task/take/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_mark_task_done(
            self, async_public_client,
            test_user, db_session):
        task = Task(
            description='Test task 2',
            deadline=date(2025, 8, 16),
            status=TaskStatus.in_progress,
            assigned_to=1
        )
        db_session.add(task)
        await db_session.commit()
        response = await async_public_client.put('task/done/2')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_delete_task_by_staff(self, async_public_client):
        response = await async_public_client.delete('task/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

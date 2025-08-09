import pytest
from fastapi import status
from sqlalchemy import select, exists
from ..models import Comment, User
from ..routers.auth import bcrypt_context


@pytest.mark.asyncio
async def test_create_comment(
        async_client, test_task, test_user,  db_session):
    payload = {
        'text': 'test comment',
    }
    response = await async_client.post('/comment/1', json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    created_comment = await db_session.scalar(
        select(Comment).where(Comment.id == 1))
    assert created_comment.text == payload['text']
    assert created_comment.user_id == 1
    assert created_comment.task_id == 1


@pytest.mark.asyncio
async def test_create_comment_task_not_exist(
        async_client, test_user):
    payload = {
        'text': 'test comment',
    }
    response = await async_client.post('/comment/99', json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'There is no task found'}


@pytest.mark.asyncio
async def test_update_comment(async_client, db_session, test_comment):
    response = await async_client.put('/comment/1', json={
        'text': 'New comment text'
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    comment = await db_session.scalar(select(Comment).where(
        Comment.id == 1
    ))
    assert comment.text == 'New comment text'


@pytest.mark.asyncio
async def test_update_another_user_comment(
        async_client, db_session, test_task, test_comment):
    another_user = User(
        name='test_user_2',
        hashed_password=bcrypt_context.hash('test123'),
        email='test2@example.com'
    )
    db_session.add(another_user)
    await db_session.commit()

    comment = Comment(
        text='New comment from user 2',
        task_id=1,
        user_id=2
    )
    db_session.add(comment)
    await db_session.commit()

    response = await async_client.put('/comment/2', json={
        'text': 'New comment text'
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        'detail': 'You do not have permission to perform this action'
    }
    updated_comment = await db_session.scalar(
        select(Comment).where(Comment.id == 2)
    )
    assert updated_comment.text == 'New comment from user 2'


@pytest.mark.asyncio
async def test_update_comment_not_exist(async_client):
    response = await async_client.put('/comment/99', json={
        'text': 'New comment text'
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'There is no comment found'
    }


@pytest.mark.asyncio
async def test_delete_task(async_client, test_comment, db_session):
    response = await async_client.delete('/comment/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await db_session.scalar(select(exists().where(
        Comment.id == 1
    ))) is False


@pytest.mark.asyncio
async def test_delete_another_user_comment(
        async_client, db_session, test_task, test_comment):
    another_user = User(
        name='test_user_2',
        hashed_password=bcrypt_context.hash('test123'),
        email='test2@example.com'
    )
    db_session.add(another_user)
    await db_session.commit()

    comment = Comment(
        text='New comment from user 2',
        task_id=1,
        user_id=2
    )
    db_session.add(comment)
    await db_session.commit()

    response = await async_client.delete('/comment/2')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        'detail': 'You do not have permission to perform this action'
    }


@pytest.mark.asyncio
async def test_delete_comment_not_exist(async_client):
    response = await async_client.delete('/comment/99')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'There is no comment found'
    }

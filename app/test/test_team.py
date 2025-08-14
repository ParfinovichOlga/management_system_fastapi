import pytest
from fastapi import status
from sqlalchemy import select, exists
from ..models import Team, User
from ..schemas import TeamOut
from sqlalchemy.orm import selectinload
from ..routers.auth import bcrypt_context


class TestTeamAdminUser:
    @pytest.mark.asyncio
    async def test_create_team(self, async_client_admin, db_session):
        payload = {'name': 'tesT tEAm'}
        response = await async_client_admin.post(
            '/team/', json=payload
        )
        assert response.status_code == status.HTTP_201_CREATED
        created_team = await db_session.scalar(
            select(Team).where(Team.id == 1)
        )
        assert created_team.name == 'Test team'

    @pytest.mark.asyncio
    async def test_get_teams(
            self, async_client_admin, test_teams, db_session):
        response = await async_client_admin.get('/team/teams')
        assert response.status_code == status.HTTP_200_OK
        teams = await db_session.scalars(select(Team))
        teams = teams.all()
        assert len(response.json()) == len(teams) == 2
        assert response.json()[0]['name'] == teams[0].name
        assert response.json()[1]['name'] == teams[1].name

    @pytest.mark.asyncio
    async def test_get_team_detail(
            self, async_client_admin, test_teams, db_session):
        response = await async_client_admin.get('/team/2')
        assert response.status_code == status.HTTP_200_OK
        team1 = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 2))
        team_out = TeamOut.model_validate(team1).model_dump()
        assert response.json() == team_out

    @pytest.mark.asyncio
    async def test_get_team_not_exist(
            self, async_client_admin):
        response = await async_client_admin.get('/team/1')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    @pytest.mark.asyncio
    async def test_get_my_team(
            self, async_client_admin):
        response = await async_client_admin.get('/team/my_team')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    @pytest.mark.asyncio
    async def test_add_members_to_team(
             self, async_client_admin, test_teams, db_session):
        member1 = User(
            name='user1',
            hashed_password=bcrypt_context.hash('test123'),
            email='test1@example.com'
        )
        member2 = User(
            name='user2',
            hashed_password=bcrypt_context.hash('test123'),
            email='test2@example.com'
        )
        db_session.add(member1)
        db_session.add(member2)
        await db_session.commit()

        response = await async_client_admin.put(
            'team/2', json={'user_ids': [2, 3]}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        team = await db_session.scalar(select(Team).where(
            Team.id == 2))
        assert len(team.members) == 2
        assert 2 in [m.id for m in team.members]
        assert 3 in [m.id for m in team.members]
        assert 1 not in [m.id for m in team.members]

    @pytest.mark.asyncio
    async def test_add_not_existing_member_to_team(
             self, async_client_admin, test_teams, db_session):
        response = await async_client_admin.put(
            'team/2', json={'user_ids': [99]}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'User with 99 id not found'}
        team = await db_session.scalar(
            select(Team).where(Team.id == 2)
        )
        assert len(team.members) == 1
        assert team.members[0].id == 1

    @pytest.mark.asyncio
    async def test_add_2_managers_to_team(
             self, async_client_admin, test_teams, db_session):
        member1 = User(
            name='user1',
            hashed_password=bcrypt_context.hash('test123'),
            email='test1@example.com',
            role='manager'
        )
        member2 = User(
            name='user2',
            hashed_password=bcrypt_context.hash('test123'),
            email='test2@example.com',
            role='manager'
        )
        db_session.add(member1)
        db_session.add(member2)
        await db_session.commit()

        response = await async_client_admin.put(
            'team/1', json={'user_ids': [2, 3]}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'You try to add 2 managers at the team'
            }
        team = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 1))
        assert len(team.members) == 0

    @pytest.mark.asyncio
    async def test_add_user_to_a_few__teams(
             self, async_client_admin, test_teams, db_session):

        response = await async_client_admin.put(
            'team/1', json={'user_ids': [1]}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        team = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 1))
        assert len(team.members) == 0

    @pytest.mark.asyncio
    async def test_clear_team_members(
             self, async_client_admin, test_teams, db_session):
        team = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 2))
        assert len(team.members) == 1
        response = await async_client_admin.put(
            'team/2', json={'user_ids': []}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        team = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 2))
        assert len(team.members) == 0

    @pytest.mark.asyncio
    async def test_update_team_name(
            self,  async_client_admin, test_teams, db_session):
        response = await async_client_admin.put(
            'team/1/change_name', json={'name': 'TEST'}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        team = await db_session.scalar(
            select(Team).where(Team.id == 1)
        )
        assert team.name == 'Test'

        response1 = await async_client_admin.put(
            'team/2/change_name', json={'name': 'TEST'}
        )
        assert response1.status_code == status.HTTP_400_BAD_REQUEST
        assert response1.json() == {
            'detail': 'Team with this name already exists'
        }

        response2 = await async_client_admin.put(
            'team/99/change_name', json={'name': 'TEST'}
        )
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        assert response2.json() == {
            'detail': 'Team not found'
        }

    @pytest.mark.asyncio
    async def test_delete_team(
             self,  async_client_admin, test_teams, db_session):
        response = await async_client_admin.delete('team/1')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await db_session.scalar(
            select(exists().where(Team.id == 1))) is False

    @pytest.mark.asyncio
    async def test_delete_team_not_exist(
             self,  async_client_admin,):
        response = await async_client_admin.delete('team/1')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Team not found.'}


class TestTeamAuthenticatedUser:
    @pytest.mark.asyncio
    async def test_create_team(self, async_client, db_session):
        payload = {'name': 'tesT tEAm'}
        response = await async_client.post(
            '/team/', json=payload
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }

    @pytest.mark.asyncio
    async def test_get_teams(
            self, async_client, test_teams, db_session):
        response = await async_client.get('/team/teams')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }

    @pytest.mark.asyncio
    async def test_get_team_detail(
            self, async_client, test_teams, db_session):
        response = await async_client.get('/team/1')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'You do not have permission to perform this action'
        }

    @pytest.mark.asyncio
    async def test_get_my_team(
            self, async_client, test_teams, db_session):
        response = await async_client.get('/team/my_team')
        assert response.status_code == status.HTTP_200_OK
        team = await db_session.scalar(
            select(Team).options(
                selectinload(Team.members)
                ).where(Team.id == 2))
        team_out = TeamOut.model_validate(team).model_dump()
        assert response.json() == team_out

    @pytest.mark.asyncio
    async def test_add_members_to_team(
             self, async_client, test_teams, db_session):
        member1 = User(
            name='user1',
            hashed_password=bcrypt_context.hash('test123'),
            email='test1@example.com'
        )
        db_session.add(member1)
        await db_session.commit()

        response = await async_client.put(
            'team/2', json={'user_ids': [2]}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_team_name(
            self,  async_client, test_teams, db_session):
        response = await async_client.put(
            'team/1/change_name', json={'name': 'TEST'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_team(
             self,  async_client, test_teams, db_session):
        response = await async_client.delete('team/1')
        assert response.status_code == status.HTTP_403_FORBIDDEN

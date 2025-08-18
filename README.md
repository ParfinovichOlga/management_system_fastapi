# management_system_fastapi
All-in-one platform to organize your team, tasks, and meetings.

### Key features:

- **Team management** – assign managers, set subordinates, and keep your hierarchy structured (admin only).
- **Task management** – create, assign, track, and update tasks; set statuses; add to your personal to-do list (managers only can create/update/delete tasks).
- **Collaboration** – comment on tasks and stay connected with your team.
- **Meetings** – schedule and cancel meetings with automatic conflict detection.
- **User accounts** – simple registration, login, logout, profile updates, and account deletion.
- **Task evaluation** – assess completed work and review evaluation history.
- **Productivity view** – see today’s and this month’s tasks at a glance.

## Project structure

- **alembic** – for database migrations

- **app/**
    - **backend/** – database configuration
    - **crud/** – processing database operations
    - **routes/** – FastAPI endpoints
    - **test/** – router tests
    - **admin_views.py** – admin panel
    - **create_admin.py** – setup for superuser
    - **main.py** – project configuration
    - **models.py** – database models (tables)
    - **schemas.py** – Pydantic validation

## Installation


- git clone git@github.com:ParfinovichOlga/management_system_fastapi.git
- docker-compose up

## Usage

- See the API Swagger documentation on [http://localhost:8001/docs](http://localhost:8001/docs) when the Docker container is running
- Admin panel: [http://localhost:8001/admin/](http://localhost:8001/admin/)
- Access pgadmin at http://localhost:5050

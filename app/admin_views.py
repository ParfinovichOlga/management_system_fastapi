from sqladmin import ModelView, Admin
from .models import (
    User, Task, Meeting,
    Comment, Evaluation, Team
)
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from .backend.db import async_session
from passlib.hash import bcrypt
from config import ADMIN_SECRET_KEY


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        name = form.get("username")
        password = form.get("password")

        async with async_session() as db:
            user = await db.scalar(select(User).where(User.name == name))

            if user and bcrypt.verify(
                    password, user.hashed_password) and user.role == 'admin':
                request.session.update({"user_id": user.id})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False
        async with async_session() as db:
            user = await db.scalar(select(User).where(User.id == user_id))
            return user is not None and user.role == "admin"


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email,
                   User.role, User.is_active, User.team_id]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.id, User.name, User.team_id]
    form_excluded_columns = [User.tasks, User.meetings]
    name_plural = "Users"


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.description, Task.deadline, Task.assigned_to]
    column_sortable_list = [Task.deadline]
    column_searchable_list = [Task.description]

    form_include_pk = False
    name_plural = "Tasks"


class MeetingAdmin(ModelView, model=Meeting):
    column_list = [Meeting.id, Meeting.title,
                   Meeting.date, Meeting.user_id, Meeting.participants]
    column_sortable_list = [Meeting.date]
    column_searchable_list = [Meeting.date, Meeting.title, Meeting.user_id]
    name_plural = "Meetings"

    can_create = False
    can_edit = False
    can_delete = False


class CommentAdmin(ModelView, model=Comment):
    column_list = [
        Comment.id, Comment.author,
        Comment.date, Comment.task_id, Comment.text]
    column_sortable_list = [Comment.date, Comment.id]
    column_searchable_list = [Comment.task_id]

    name_plural = "Comments"


class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = [
        Evaluation.id, Evaluation.date, Evaluation.grade,
        Evaluation.task, Evaluation.employee
    ]
    column_sortable_list = [Evaluation.date]
    column_searchable_list = [Evaluation.employee, Evaluation.task]
    name_plural = "Evaluations"


class TeamAdmin(ModelView, model=Team):
    column_list = [
        Team.id, Team.name, Team.members
    ]
    column_sortable_list = [Team.id]
    column_searchable_list = [Team.name]
    name_plural = "Teams"


auth_backend = AdminAuth(secret_key=ADMIN_SECRET_KEY)


def setup_admin(app, engine):
    admin = Admin(app, engine, authentication_backend=auth_backend)
    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(EvaluationAdmin)
    admin.add_view(MeetingAdmin)

from app.backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Enum, Text, Date, DateTime
from sqlalchemy.sql import text

import enum
from typing import List
from datetime import date, datetime, timezone


class Roles(enum.Enum):
    admin = 'admin'
    manager = 'manager'
    staff = 'staff'


class TaskStatus(enum.Enum):
    opened = 'opened'
    in_progress = 'in progress'
    done = 'done'


class Team(Base):
    __tablename__ = 'team'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    members: Mapped[List['User']] = relationship(back_populates='team')

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(
        default='staff', server_default=text("'staff'"))
    tasks: Mapped[List['Task']] = relationship(back_populates='assigned_user')
    comments: Mapped[List['Comment']] = relationship(back_populates='author')
    team_id: Mapped['Team'] = mapped_column(
        ForeignKey('team.id', ondelete='SET NULL'),
        nullable=True, default=None)
    team: Mapped['Team'] = relationship(back_populates='members')

    def __str__(self):
        return self.name


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assigned_to: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='SET NULL'), nullable=True, default=None
        )
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name='task_status'),
        nullable=False, default=TaskStatus.opened,
        server_default=text("'opened'")
    )
    deadline: Mapped[date] = mapped_column(Date)
    assigned_user: Mapped['User'] = relationship(back_populates='tasks')
    comments: Mapped[List['Comment']] = relationship(back_populates='task')

    def __str__(self):
        return self.description


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    task_id: Mapped[int] = mapped_column(
        ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    author: Mapped['User'] = relationship(back_populates='comments')
    task: Mapped['Task'] = relationship(back_populates='comments')

    def __str__(self):
        return self.text

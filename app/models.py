from app.backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Enum, Text, Date
from sqlalchemy.sql import text

import enum
from typing import List
from datetime import date


class TaskStatus(enum.Enum):
    opened = 'opened'
    in_progress = 'in progress'
    done = 'done'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default='staff')
    tasks: Mapped[List['Task']] = relationship(back_populates='user')


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
    user: Mapped['User'] = relationship(back_populates='tasks')
    
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import date
from .models import TaskStatus
from typing import Optional


class Roles(Enum):
    admin = 'admin'
    manager = 'manager'
    staff = 'staff'


class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, examples=['Enter your password']
        )
    name: str = Field(max_length=150, examples=['Enter your name'])


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8)


class CreateTask(BaseModel):
    description: str = Field(max_length=500)
    deadline: date


class UpdateTask(CreateTask):
    status: TaskStatus
    assigned_to: Optional[str] = None

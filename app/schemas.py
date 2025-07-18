from pydantic import BaseModel, Field, EmailStr
from datetime import date
from .models import TaskStatus
from typing import Optional


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
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None


class RequestedComment(BaseModel):
    text: str = Field(max_length=2000)

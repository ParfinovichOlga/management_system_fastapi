from pydantic import BaseModel, Field, EmailStr
from enum import Enum


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

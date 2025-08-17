from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import date, datetime, timezone
from .models import TaskStatus
from typing import Optional, List


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    role: str
    team_id: Optional[int]

    model_config = ConfigDict(
        from_attributes=True
    )


class UserOutForMeeting(BaseModel):
    email: EmailStr
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, examples=['Enter your password']
        )
    name: str = Field(max_length=150, examples=['Enter your name'])


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8)


class TaskOut(BaseModel):
    description: str
    deadline: date

    model_config = ConfigDict(
        from_attributes=True,
    )


class CreateTask(BaseModel):
    description: str = Field(max_length=500)
    deadline: date


class UpdateTask(CreateTask):
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None


class RequestedComment(BaseModel):
    text: str = Field(max_length=2000)


class TeamOut(BaseModel):
    id: int
    name: str
    members: List[UserOut]

    model_config = ConfigDict(
        from_attributes=True
    )


class CreateTeam(BaseModel):
    name: str = Field(max_length=100)

    @field_validator('name', mode='before')
    @classmethod
    def process_name(cls, name: str):
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")

        name = name.split()
        name[0] = name[0].title().strip()
        for i in range(1, len(name)):
            name[i] = name[i].lower().strip()
        name = ' '.join(name)
        return name


class UsersToAdd(BaseModel):
    user_ids: List[int]


class CreateEvaluation(BaseModel):
    grade: int = Field(ge=1, le=5)


class EvaluationOut(BaseModel):
    grade: int
    date: datetime
    task: TaskOut

    model_config = ConfigDict(
        from_attributes=True
    )


class CreateMeeting(BaseModel):
    date: datetime
    title: str = Field(max_length=200)
    description: str = Field(max_length=500)
    participants: List[int] = Field(..., min_length=1)

    @field_validator('date')
    def validate_future_date(cls, date: datetime):
        if date < datetime.now(timezone.utc):
            raise ValueError("Meeting date must be in the future")

        date = date.replace(second=0, microsecond=0)
        return date


class MeetingOut(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    participants: List[UserOutForMeeting]

    model_config = ConfigDict(
        from_attributes=True
    )

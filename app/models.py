from app.backend.db import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] 
    name: Mapped[str]    
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] 


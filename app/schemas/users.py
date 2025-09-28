from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel


class UserBase(SQLModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    ai_analysis_json: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    ai_analysis_json: Optional[str] = None


class UserRead(UserBase):
    id: int

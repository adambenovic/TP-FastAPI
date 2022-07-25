from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    name: Optional[str]
    surname: Optional[str]


class User(UserBase):
    id: UUID
    active: bool

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class ResetPassword(BaseModel):
    email: str
    language: str


class UpdatePassword(BaseModel):
    password: str
    token: UUID

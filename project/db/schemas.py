from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=3, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class AuthOut(BaseModel):
    user_id: int
    username: str
    token: str
    token_type: str = "Bearer"
    expires_at: datetime


class TodoCreate(BaseModel):
    task: str = Field(min_length=1, max_length=500)


class TodoUpdate(BaseModel):
    task: Optional[str] = Field(default=None, min_length=1, max_length=500)
    is_completed: Optional[bool] = None


class TodoOut(BaseModel):
    id: int
    task: str
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

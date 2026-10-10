from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    """The two access levels in this API."""
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    role: Role = Role.user


class UserPublic(BaseModel):
    """What we return to clients - never includes the password hash."""
    username: str
    role: Role


class UserInDB(UserPublic):
    """Internal representation, stored server-side only."""
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    role: Role

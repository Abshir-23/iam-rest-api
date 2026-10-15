from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    """De to tilgangsnivåene i dette API-et."""
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    role: Role = Role.user


class UserPublic(BaseModel):
    """Det vi returnerer til klienter, inneholder aldri passordhashen."""
    username: str
    role: Role


class UserInDB(UserPublic):
    """Intern representasjon, lagres bare på serveren."""
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    role: Role

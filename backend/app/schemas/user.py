from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from app.models.user import UserRole


class UserPublic(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    first_name: str
    last_name: str

    role: UserRole

    institution: str | None = None
    country: str | None = None

    expertise: str | None = None
    bio: str | None = None

    orcid: str | None = None
    website: str | None = None
    github: str | None = None

    collaboration_open: bool

    created_at: datetime


class UserMe(UserPublic):
    email: EmailStr

    is_active: bool

    is_email_verified: bool

    email_verified_at: datetime | None = None


class RegisterRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=10,
        max_length=128,
    )

    first_name: str = Field(
        min_length=2,
        max_length=120,
    )

    last_name: str = Field(
        min_length=2,
        max_length=120,
    )

    country: str | None = None

    institution: str | None = None

    requested_role: Literal[
        "reader",
        "researcher",
        "contributor",
    ] = "researcher"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

    institution: str | None = None
    country: str | None = None

    expertise: str | None = None
    bio: str | None = None

    orcid: str | None = None
    website: str | None = None
    github: str | None = None

    collaboration_open: bool | None = None


class AdminRoleUpdate(BaseModel):
    role: UserRole
    is_active: bool | None = None
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    first_name: str
    last_name: str
    role: UserRole
    institution: str | None = None
    country: str | None = None
    professional_headline: str | None = None
    expertise: str | None = None
    bio: str | None = None
    research_interests: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    technical_stack: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    featured_publication_ids: list[str] = Field(default_factory=list)
    orcid: str | None = None
    website: str | None = None
    github: str | None = None
    linkedin: str | None = None
    google_scholar: str | None = None
    researchgate: str | None = None
    collaboration_open: bool
    created_at: datetime


class UserMe(UserPublic):
    email: EmailStr
    is_active: bool
    is_email_verified: bool
    email_verified_at: datetime | None = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    first_name: str = Field(min_length=2, max_length=120)
    last_name: str = Field(min_length=2, max_length=120)
    country: str | None = None
    institution: str | None = None
    requested_role: Literal["reader", "researcher", "contributor"] = "researcher"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=120)
    last_name: str | None = Field(default=None, min_length=2, max_length=120)
    institution: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=120)
    professional_headline: str | None = Field(default=None, max_length=180)
    expertise: str | None = None
    bio: str | None = None
    research_interests: list[str] | None = None
    tools: list[str] | None = None
    technical_stack: list[str] | None = None
    languages: list[str] | None = None
    featured_publication_ids: list[str] | None = None
    orcid: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=500)
    github: str | None = Field(default=None, max_length=500)
    linkedin: str | None = Field(default=None, max_length=500)
    google_scholar: str | None = Field(default=None, max_length=500)
    researchgate: str | None = Field(default=None, max_length=500)
    collaboration_open: bool | None = None


class AdminRoleUpdate(BaseModel):
    role: UserRole
    is_active: bool | None = None

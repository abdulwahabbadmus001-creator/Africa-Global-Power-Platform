from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.publication import PublicationStatus
from app.schemas.user import UserPublic


SubmissionMethod = Literal["form", "upload", "both"]


class PublicationCreate(BaseModel):
    title: str = Field(min_length=3, max_length=400)
    abstract: str = ""
    body: str = ""
    publication_type: str = "analysis"
    submission_method: SubmissionMethod = "form"
    topic: str
    region: str | None = None
    country: str | None = None
    keywords: list[str] = Field(default_factory=list)
    references: list[dict] = Field(default_factory=list)
    methodology: str | None = None
    limitations: str | None = None
    policy_implications: str | None = None


class PublicationUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    body: str | None = None
    publication_type: str | None = None
    submission_method: SubmissionMethod | None = None
    topic: str | None = None
    region: str | None = None
    country: str | None = None
    keywords: list[str] | None = None
    references: list[dict] | None = None
    methodology: str | None = None
    limitations: str | None = None
    policy_implications: str | None = None
    change_note: str | None = None


class PublicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    author_id: UUID
    assigned_editor_id: UUID | None
    title: str
    slug: str
    abstract: str
    body: str
    publication_type: str
    submission_method: str
    topic: str
    region: str | None
    country: str | None
    keywords: list
    references: list
    methodology: str | None
    limitations: str | None
    policy_implications: str | None
    status: PublicationStatus
    current_version: int
    scheduled_for: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: UserPublic | None = None


class EditorialQueueItem(BaseModel):
    id: UUID
    assigned_editor_id: UUID | None
    title: str
    publication_type: str
    submission_method: str
    topic: str
    region: str | None
    country: str | None
    status: PublicationStatus
    current_version: int
    created_at: datetime
    updated_at: datetime
    author: UserPublic | None = None


class EditorialTransition(BaseModel):
    to_status: PublicationStatus
    note: str | None = None
    assigned_editor_id: UUID | None = None
    scheduled_for: datetime | None = None

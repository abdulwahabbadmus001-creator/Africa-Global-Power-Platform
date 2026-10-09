from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    summary: str = ""
    description: str = ""
    category: str
    region: str | None = None
    country: str | None = None
    source_name: str
    source_url: str
    download_url: str | None = None
    license_name: str | None = None
    tags: list[str] = Field(default_factory=list)
    coverage_start: date | None = None
    coverage_end: date | None = None
    is_published: bool = True


class DatasetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=300)
    summary: str | None = None
    description: str | None = None
    category: str | None = None
    region: str | None = None
    country: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    download_url: str | None = None
    license_name: str | None = None
    tags: list[str] | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    is_published: bool | None = None


class DatasetOut(DatasetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime


class PolicyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=400)
    country: str
    institution: str
    policy_area: str
    status: str
    summary: str = ""
    agp_analysis: str = ""
    source_url: str
    published_date: date | None = None
    effective_date: date | None = None
    tags: list[str] = Field(default_factory=list)
    is_published: bool = True


class PolicyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=400)
    country: str | None = None
    institution: str | None = None
    policy_area: str | None = None
    status: str | None = None
    summary: str | None = None
    agp_analysis: str | None = None
    source_url: str | None = None
    published_date: date | None = None
    effective_date: date | None = None
    tags: list[str] | None = None
    is_published: bool | None = None


class PolicyOut(PolicyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    created_by_id: UUID
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class OpportunityCreate(BaseModel):
    title: str = Field(min_length=3, max_length=350)
    organization: str
    category: str
    country: str | None = None
    location_mode: str = "unspecified"
    deadline: date | None = None
    summary: str = ""
    url: str
    tags: list[str] = Field(default_factory=list)
    is_published: bool = True


class OpportunityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=350)
    organization: str | None = None
    category: str | None = None
    country: str | None = None
    location_mode: str | None = None
    deadline: date | None = None
    summary: str | None = None
    url: str | None = None
    tags: list[str] | None = None
    is_published: bool | None = None


class OpportunityOut(OpportunityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime


class RoomCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str = ""
    topic: str
    visibility: str = Field(
        default="public",
        pattern="^(public|private)$",
    )
    join_policy: str = Field(
        default="open",
        pattern="^(open|invite)$",
    )


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    title: str
    slug: str
    description: str
    topic: str
    visibility: str
    join_policy: str
    created_at: datetime
    updated_at: datetime
    member_count: int = 0
    is_member: bool = False


class RoomPostCreate(BaseModel):
    body: str = Field(
        min_length=1,
        max_length=10000,
    )
    resource_url: str | None = None


class RoomPostOut(BaseModel):
    id: UUID
    room_id: UUID
    author_id: UUID
    author_name: str
    body: str
    resource_url: str | None
    created_at: datetime


class RoomInvite(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=320,
    )

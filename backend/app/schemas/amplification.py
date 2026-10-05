from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


ShareChannel = Literal[
    "linkedin",
    "x",
    "facebook",
    "whatsapp",
    "email",
    "medium",
    "researchgate",
    "academia",
    "github",
    "copy",
]


class ShareLinkRequest(BaseModel):
    channel: ShareChannel

    context: str = Field(
        default="public_page",
        max_length=80,
    )

    message_override: str | None = Field(
        default=None,
        max_length=1500,
    )


class ShareLinkResponse(BaseModel):
    event_id: UUID

    channel: str

    canonical_url: str

    tracked_url: str

    share_url: str

    suggested_text: str

    mode: str

    manual_instruction: str | None = None


class ShareClickRequest(BaseModel):
    session_id: str = Field(
        min_length=8,
        max_length=200,
    )

    referrer_host: str | None = Field(
        default=None,
        max_length=500,
    )


class ShareClickResponse(BaseModel):
    recorded: bool


class AmplificationMetricsOut(BaseModel):
    publication_id: UUID

    title: str

    slug: str

    published_at: datetime | None

    share_actions: int

    referral_clicks: int

    channels: dict[str, int]


class InstitutionalAnnouncementOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    publication_id: UUID

    created_by_id: UUID

    message: str

    channels: list

    distributed_channels: list

    status: str

    distributed_at: datetime | None

    created_at: datetime

    updated_at: datetime


class InstitutionalAnnouncementUpdate(
    BaseModel
):
    message: str = Field(
        min_length=20,
        max_length=3000,
    )

    channels: list[str] = Field(
        default_factory=list,
    )


class InstitutionalDistributionRequest(
    BaseModel
):
    channels: list[str] = Field(
        min_length=1,
    )


class EditorialAmplificationQueueItem(
    BaseModel
):
    publication_id: UUID

    title: str

    slug: str

    author_name: str

    published_at: datetime | None

    announcement: (
        InstitutionalAnnouncementOut
        | None
    )
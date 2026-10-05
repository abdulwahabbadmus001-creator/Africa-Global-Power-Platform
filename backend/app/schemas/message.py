from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserPublic


class MessageCreate(BaseModel):
    recipient_id: UUID
    subject: str = Field(min_length=2, max_length=240)
    body: str = Field(min_length=2, max_length=10000)
    context_type: str | None = None
    context_id: str | None = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    subject: str
    body: str
    context_type: str | None
    context_id: str | None
    is_read: bool
    created_at: datetime
    sender: UserPublic | None = None
    recipient: UserPublic | None = None

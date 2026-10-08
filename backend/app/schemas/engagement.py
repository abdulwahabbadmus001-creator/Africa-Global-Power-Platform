from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserPublic

class ActionResponse(BaseModel):
    message: str

class IdList(BaseModel):
    ids: list[UUID]

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    actor_id: UUID | None
    kind: str
    title: str
    body: str
    link: str | None
    is_read: bool
    created_at: datetime
    actor: UserPublic | None = None

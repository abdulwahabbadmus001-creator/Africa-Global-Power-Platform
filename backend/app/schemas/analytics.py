from uuid import UUID
from pydantic import BaseModel


class AnalyticsEventCreate(BaseModel):
    publication_id: UUID
    event_type: str
    session_id: str | None = None
    referrer_host: str | None = None


class PublicationAnalytics(BaseModel):
    publication_id: UUID
    views: int = 0
    unique_readers: int = 0
    saves: int = 0
    shares: int = 0
    downloads: int = 0
    source_clicks: int = 0

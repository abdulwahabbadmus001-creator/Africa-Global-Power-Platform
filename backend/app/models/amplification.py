import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ResearchShareEvent(Base):
    __tablename__ = "research_share_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    publication_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "publications.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    sharer_user_id: Mapped[
        uuid.UUID | None
    ] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    channel: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    context: Mapped[str] = mapped_column(
        String(80),
        default="public_page",
        index=True,
    )

    message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
        index=True,
    )


class ResearchShareClick(Base):
    __tablename__ = "research_share_clicks"

    __table_args__ = (
        UniqueConstraint(
            "share_event_id",
            "session_id_hash",
            name=(
                "uq_research_share_click_event_session"
            ),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    share_event_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        ForeignKey(
            "research_share_events.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    session_id_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    referrer_host: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )

    user_agent: Mapped[
        str | None
    ] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
        index=True,
    )


class InstitutionalAnnouncement(Base):
    __tablename__ = "institutional_announcements"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    publication_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        ForeignKey(
            "publications.id",
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
    )

    created_by_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
    )

    channels: Mapped[list] = mapped_column(
        JSONB,
        default=list,
    )

    distributed_channels: Mapped[
        list
    ] = mapped_column(
        JSONB,
        default=list,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        default="draft",
        index=True,
    )

    distributed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
        onupdate=lambda: datetime.now(
            timezone.utc
        ),
    )
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PublicationStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    desk_review = "desk_review"
    editorial_review = "editorial_review"
    revision_requested = "revision_requested"
    source_check = "source_check"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    rejected = "rejected"


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    assigned_editor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(400))
    slug: Mapped[str] = mapped_column(String(450), unique=True, index=True)
    abstract: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    publication_type: Mapped[str] = mapped_column(String(80), default="analysis")
    submission_method: Mapped[str] = mapped_column(String(30), default="form", index=True)
    topic: Mapped[str] = mapped_column(String(120), index=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    keywords: Mapped[list] = mapped_column(JSONB, default=list)
    references: Mapped[list] = mapped_column(JSONB, default=list)
    methodology: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    policy_implications: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, name="publication_status"),
        default=PublicationStatus.draft,
        index=True,
    )
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    scheduled_for: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    author = relationship("User", back_populates="publications", foreign_keys=[author_id])
    assigned_editor = relationship("User", foreign_keys=[assigned_editor_id])
    versions = relationship(
        "PublicationVersion", back_populates="publication", cascade="all, delete-orphan"
    )
    editorial_actions = relationship(
        "EditorialAction", back_populates="publication", cascade="all, delete-orphan"
    )


class PublicationVersion(Base):
    __tablename__ = "publication_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    publication_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("publications.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(400))
    abstract: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    publication = relationship("Publication", back_populates="versions")

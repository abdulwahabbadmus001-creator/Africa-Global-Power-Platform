import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.session import Base


class UserRole(str, enum.Enum):
    reader = "reader"
    researcher = "researcher"
    contributor = "contributor"
    reviewer = "reviewer"
    editor = "editor"
    senior_editor = "senior_editor"
    managing_editor = "managing_editor"
    super_admin = "super_admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(500),
    )

    first_name: Mapped[str] = mapped_column(
        String(120),
    )

    last_name: Mapped[str] = mapped_column(
        String(120),
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
        ),
        default=UserRole.reader,
        index=True,
    )

    institution: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[
        str | None
    ] = mapped_column(
        String(120),
        nullable=True,
    )

    expertise: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    bio: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    orcid: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True,
    )

    website: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )

    github: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )

    collaboration_open: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=True,
    )

    is_active: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=True,
    )

    is_email_verified: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )

    email_verified_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    editor_mfa_enabled: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )

    editor_mfa_generation: Mapped[
        int
    ] = mapped_column(
        Integer,
        default=1,
    )

    editor_mfa_enabled_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    publications = relationship(
        "Publication",
        back_populates="author",
        foreign_keys=(
            "Publication.author_id"
        ),
    )
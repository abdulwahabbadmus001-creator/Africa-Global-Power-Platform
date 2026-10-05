import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.session import Base


class AuthChallenge(Base):
    __tablename__ = "auth_challenges"

    id: Mapped[
        uuid.UUID
    ] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    purpose: Mapped[
        str
    ] = mapped_column(
        String(80),
        index=True,
    )

    code_hash: Mapped[
        str
    ] = mapped_column(
        String(128),
    )

    attempts: Mapped[
        int
    ] = mapped_column(
        Integer,
        default=0,
    )

    max_attempts: Mapped[
        int
    ] = mapped_column(
        Integer,
        default=5,
    )

    expires_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
    )

    consumed_at: Mapped[
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
        index=True,
    )


class AuthAuditEvent(Base):
    __tablename__ = "auth_audit_events"

    id: Mapped[
        uuid.UUID
    ] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[
        uuid.UUID | None
    ] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    email: Mapped[
        str | None
    ] = mapped_column(
        String(320),
        nullable=True,
        index=True,
    )

    event_type: Mapped[
        str
    ] = mapped_column(
        String(100),
        index=True,
    )

    success: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        default=False,
    )

    ip_address: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    user_agent: Mapped[
        str | None
    ] = mapped_column(
        String(1000),
        nullable=True,
    )

    details: Mapped[
        dict
    ] = mapped_column(
        JSONB,
        default=dict,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
        index=True,
    )


class MfaRecoveryCode(Base):
    __tablename__ = "mfa_recovery_codes"

    id: Mapped[
        uuid.UUID
    ] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    code_hash: Mapped[
        str
    ] = mapped_column(
        String(128),
        index=True,
    )

    used_at: Mapped[
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
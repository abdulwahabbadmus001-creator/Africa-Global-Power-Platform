"""AGP Authentication & Security V2 foundation.

Revision ID: 0002_authentication_v2
Revises: 0001_initial_schema
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_authentication_v2"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # USERS: EMAIL VERIFICATION
    # ---------------------------------------------------------

    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "email_verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_is_email_verified",
        "users",
        ["is_email_verified"],
        unique=False,
    )

    # Existing development accounts existed before email
    # verification was introduced. Mark them as verified.
    op.execute(
        """
        UPDATE users
        SET
            is_email_verified = TRUE,
            email_verified_at = NOW()
        """
    )

    # ---------------------------------------------------------
    # AUTH CHALLENGES
    # ---------------------------------------------------------

    op.create_table(
        "auth_challenges",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "purpose",
            sa.String(length=80),
            nullable=False,
        ),

        sa.Column(
            "code_hash",
            sa.String(length=128),
            nullable=False,
        ),

        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_auth_challenges_user_id",
        "auth_challenges",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_challenges_purpose",
        "auth_challenges",
        ["purpose"],
        unique=False,
    )

    op.create_index(
        "ix_auth_challenges_created_at",
        "auth_challenges",
        ["created_at"],
        unique=False,
    )

    # ---------------------------------------------------------
    # AUTH AUDIT LOG
    # ---------------------------------------------------------

    op.create_table(
        "auth_audit_events",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "email",
            sa.String(length=320),
            nullable=True,
        ),

        sa.Column(
            "event_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "success",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "ip_address",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "user_agent",
            sa.String(length=1000),
            nullable=True,
        ),

        sa.Column(
            "details",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_auth_audit_events_user_id",
        "auth_audit_events",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_audit_events_email",
        "auth_audit_events",
        ["email"],
        unique=False,
    )

    op.create_index(
        "ix_auth_audit_events_event_type",
        "auth_audit_events",
        ["event_type"],
        unique=False,
    )

    op.create_index(
        "ix_auth_audit_events_created_at",
        "auth_audit_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # AUTH AUDIT LOG
    # ---------------------------------------------------------

    op.drop_index(
        "ix_auth_audit_events_created_at",
        table_name="auth_audit_events",
    )

    op.drop_index(
        "ix_auth_audit_events_event_type",
        table_name="auth_audit_events",
    )

    op.drop_index(
        "ix_auth_audit_events_email",
        table_name="auth_audit_events",
    )

    op.drop_index(
        "ix_auth_audit_events_user_id",
        table_name="auth_audit_events",
    )

    op.drop_table(
        "auth_audit_events"
    )

    # ---------------------------------------------------------
    # AUTH CHALLENGES
    # ---------------------------------------------------------

    op.drop_index(
        "ix_auth_challenges_created_at",
        table_name="auth_challenges",
    )

    op.drop_index(
        "ix_auth_challenges_purpose",
        table_name="auth_challenges",
    )

    op.drop_index(
        "ix_auth_challenges_user_id",
        table_name="auth_challenges",
    )

    op.drop_table(
        "auth_challenges"
    )

    # ---------------------------------------------------------
    # USER EMAIL VERIFICATION
    # ---------------------------------------------------------

    op.drop_index(
        "ix_users_is_email_verified",
        table_name="users",
    )

    op.drop_column(
        "users",
        "email_verified_at",
    )

    op.drop_column(
        "users",
        "is_email_verified",
    )
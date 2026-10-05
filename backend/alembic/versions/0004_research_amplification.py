"""Research amplification.

Revision ID: 0004_research_amplification
Revises: 0003_editorial_mfa
"""

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


revision = (
    "0004_research_amplification"
)

down_revision = (
    "0003_editorial_mfa"
)

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_share_events",

        sa.Column(
            "id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "publication_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "sharer_user_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=True,
        ),

        sa.Column(
            "channel",
            sa.String(
                length=50
            ),
            nullable=False,
        ),

        sa.Column(
            "context",
            sa.String(
                length=80
            ),
            nullable=False,
            server_default=(
                "public_page"
            ),
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=(
                sa.func.now()
            ),
        ),

        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["publications.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["sharer_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_research_share_events_publication_id",
        "research_share_events",
        ["publication_id"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_events_sharer_user_id",
        "research_share_events",
        ["sharer_user_id"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_events_channel",
        "research_share_events",
        ["channel"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_events_context",
        "research_share_events",
        ["context"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_events_created_at",
        "research_share_events",
        ["created_at"],
        unique=False,
    )


    op.create_table(
        "research_share_clicks",

        sa.Column(
            "id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "share_event_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "session_id_hash",
            sa.String(
                length=64
            ),
            nullable=False,
        ),

        sa.Column(
            "referrer_host",
            sa.String(
                length=500
            ),
            nullable=True,
        ),

        sa.Column(
            "user_agent",
            sa.String(
                length=1000
            ),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=(
                sa.func.now()
            ),
        ),

        sa.ForeignKeyConstraint(
            ["share_event_id"],
            ["research_share_events.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "share_event_id",
            "session_id_hash",
            name=(
                "uq_research_share_click_event_session"
            ),
        ),
    )

    op.create_index(
        "ix_research_share_clicks_share_event_id",
        "research_share_clicks",
        ["share_event_id"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_clicks_session_id_hash",
        "research_share_clicks",
        ["session_id_hash"],
        unique=False,
    )

    op.create_index(
        "ix_research_share_clicks_created_at",
        "research_share_clicks",
        ["created_at"],
        unique=False,
    )


    op.create_table(
        "institutional_announcements",

        sa.Column(
            "id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "publication_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "created_by_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "channels",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),

        sa.Column(
            "distributed_channels",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),

        sa.Column(
            "status",
            sa.String(
                length=40
            ),
            nullable=False,
            server_default="draft",
        ),

        sa.Column(
            "distributed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=(
                sa.func.now()
            ),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
            server_default=(
                sa.func.now()
            ),
        ),

        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["publications.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "publication_id",
        ),
    )

    op.create_index(
        "ix_institutional_announcements_publication_id",
        "institutional_announcements",
        ["publication_id"],
        unique=True,
    )

    op.create_index(
        "ix_institutional_announcements_created_by_id",
        "institutional_announcements",
        ["created_by_id"],
        unique=False,
    )

    op.create_index(
        "ix_institutional_announcements_status",
        "institutional_announcements",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_institutional_announcements_status",
        table_name=(
            "institutional_announcements"
        ),
    )

    op.drop_index(
        "ix_institutional_announcements_created_by_id",
        table_name=(
            "institutional_announcements"
        ),
    )

    op.drop_index(
        "ix_institutional_announcements_publication_id",
        table_name=(
            "institutional_announcements"
        ),
    )

    op.drop_table(
        "institutional_announcements"
    )


    op.drop_index(
        "ix_research_share_clicks_created_at",
        table_name=(
            "research_share_clicks"
        ),
    )

    op.drop_index(
        "ix_research_share_clicks_session_id_hash",
        table_name=(
            "research_share_clicks"
        ),
    )

    op.drop_index(
        "ix_research_share_clicks_share_event_id",
        table_name=(
            "research_share_clicks"
        ),
    )

    op.drop_table(
        "research_share_clicks"
    )


    op.drop_index(
        "ix_research_share_events_created_at",
        table_name=(
            "research_share_events"
        ),
    )

    op.drop_index(
        "ix_research_share_events_context",
        table_name=(
            "research_share_events"
        ),
    )

    op.drop_index(
        "ix_research_share_events_channel",
        table_name=(
            "research_share_events"
        ),
    )

    op.drop_index(
        "ix_research_share_events_sharer_user_id",
        table_name=(
            "research_share_events"
        ),
    )

    op.drop_index(
        "ix_research_share_events_publication_id",
        table_name=(
            "research_share_events"
        ),
    )

    op.drop_table(
        "research_share_events"
    )
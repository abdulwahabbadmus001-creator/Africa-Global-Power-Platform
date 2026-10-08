"""Research profiles and reader engagement.

Revision ID: 0007_research_network
Revises: 0006_platform_features
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_research_network"
down_revision = "0006_platform_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("professional_headline", sa.String(length=180), nullable=True))
    for name in ("research_interests", "tools", "technical_stack", "languages", "featured_publication_ids"):
        op.add_column(
            "users",
            sa.Column(name, postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        )
    op.add_column("users", sa.Column("linkedin", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("google_scholar", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("researchgate", sa.String(length=500), nullable=True))

    op.create_table(
        "saved_publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "publication_id", name="uq_saved_publication_user_publication"),
    )
    op.create_index("ix_saved_publications_user_id", "saved_publications", ["user_id"], unique=False)
    op.create_index("ix_saved_publications_publication_id", "saved_publications", ["publication_id"], unique=False)

    op.create_table(
        "researcher_follows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("researcher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["researcher_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "researcher_id", name="uq_researcher_follow_pair"),
    )
    op.create_index("ix_researcher_follows_follower_id", "researcher_follows", ["follower_id"], unique=False)
    op.create_index("ix_researcher_follows_researcher_id", "researcher_follows", ["researcher_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("kind", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("link", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_actor_id", "notifications", ["actor_id"], unique=False)
    op.create_index("ix_notifications_kind", "notifications", ["kind"], unique=False)
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"], unique=False)
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"], unique=False)


def downgrade() -> None:
    for name in (
        "ix_notifications_created_at", "ix_notifications_is_read", "ix_notifications_kind",
        "ix_notifications_actor_id", "ix_notifications_user_id",
    ):
        op.drop_index(name, table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_researcher_follows_researcher_id", table_name="researcher_follows")
    op.drop_index("ix_researcher_follows_follower_id", table_name="researcher_follows")
    op.drop_table("researcher_follows")
    op.drop_index("ix_saved_publications_publication_id", table_name="saved_publications")
    op.drop_index("ix_saved_publications_user_id", table_name="saved_publications")
    op.drop_table("saved_publications")
    for name in (
        "researchgate", "google_scholar", "linkedin", "featured_publication_ids", "languages",
        "technical_stack", "tools", "research_interests", "professional_headline",
    ):
        op.drop_column("users", name)

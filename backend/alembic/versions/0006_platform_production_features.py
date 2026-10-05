"""Platform production features.

Revision ID: 0006_platform_features
Revises: 0005_research_trust_vault
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_platform_features"
down_revision = "0005_research_trust_vault"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("slug", sa.String(340), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(120), nullable=False),
        sa.Column("region", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=True),
        sa.Column("source_name", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("download_url", sa.String(1000), nullable=True),
        sa.Column("license_name", sa.String(180), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("coverage_start", sa.Date(), nullable=True),
        sa.Column("coverage_end", sa.Date(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("slug"),
    )
    for name, cols in [
        ("ix_datasets_slug", ["slug"]), ("ix_datasets_category", ["category"]),
        ("ix_datasets_region", ["region"]), ("ix_datasets_country", ["country"]),
        ("ix_datasets_created_by_id", ["created_by_id"]), ("ix_datasets_is_published", ["is_published"]),
    ]:
        op.create_index(name, "datasets", cols, unique=(name == "ix_datasets_slug"))

    op.create_table(
        "policy_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(400), nullable=False),
        sa.Column("slug", sa.String(450), nullable=False),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("institution", sa.String(255), nullable=False),
        sa.Column("policy_area", sa.String(150), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("agp_analysis", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("slug"),
    )
    for name, cols in [
        ("ix_policy_records_slug", ["slug"]), ("ix_policy_records_country", ["country"]),
        ("ix_policy_records_institution", ["institution"]), ("ix_policy_records_policy_area", ["policy_area"]),
        ("ix_policy_records_status", ["status"]), ("ix_policy_records_created_by_id", ["created_by_id"]),
        ("ix_policy_records_is_published", ["is_published"]),
    ]:
        op.create_index(name, "policy_records", cols, unique=(name == "ix_policy_records_slug"))

    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(350), nullable=False),
        sa.Column("organization", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("country", sa.String(120), nullable=True),
        sa.Column("location_mode", sa.String(80), nullable=False, server_default="unspecified"),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
    )
    for name, cols in [
        ("ix_opportunities_organization", ["organization"]), ("ix_opportunities_category", ["category"]),
        ("ix_opportunities_country", ["country"]), ("ix_opportunities_deadline", ["deadline"]),
        ("ix_opportunities_created_by_id", ["created_by_id"]), ("ix_opportunities_is_published", ["is_published"]),
    ]:
        op.create_index(name, "opportunities", cols)

    op.create_table(
        "research_rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("slug", sa.String(280), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("topic", sa.String(150), nullable=False),
        sa.Column("visibility", sa.String(30), nullable=False, server_default="public"),
        sa.Column("join_policy", sa.String(30), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_research_rooms_owner_id", "research_rooms", ["owner_id"])
    op.create_index("ix_research_rooms_slug", "research_rooms", ["slug"], unique=True)
    op.create_index("ix_research_rooms_topic", "research_rooms", ["topic"])
    op.create_index("ix_research_rooms_visibility", "research_rooms", ["visibility"])

    op.create_table(
        "research_room_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["room_id"], ["research_rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("room_id", "user_id", name="uq_research_room_member"),
    )
    op.create_index("ix_research_room_members_room_id", "research_room_members", ["room_id"])
    op.create_index("ix_research_room_members_user_id", "research_room_members", ["user_id"])

    op.create_table(
        "research_room_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resource_url", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["room_id"], ["research_rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_research_room_posts_room_id", "research_room_posts", ["room_id"])
    op.create_index("ix_research_room_posts_author_id", "research_room_posts", ["author_id"])
    op.create_index("ix_research_room_posts_created_at", "research_room_posts", ["created_at"])


def downgrade() -> None:
    op.drop_table("research_room_posts")
    op.drop_table("research_room_members")
    op.drop_table("research_rooms")
    op.drop_table("opportunities")
    op.drop_table("policy_records")
    op.drop_table("datasets")


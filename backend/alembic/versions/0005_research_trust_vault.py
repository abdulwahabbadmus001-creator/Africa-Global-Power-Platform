"""Research Trust Vault and manuscript storage.

Revision ID: 0005_research_trust_vault
Revises: 0004_research_amplification
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0005_research_trust_vault"
down_revision = "0004_research_amplification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "publications",
        sa.Column("submission_method", sa.String(length=30), nullable=False, server_default="form"),
    )
    op.create_index("ix_publications_submission_method", "publications", ["submission_method"], unique=False)

    op.create_table(
        "manuscript_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=180), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_backend", sa.String(length=30), nullable=False),
        sa.Column("storage_key", sa.String(length=1000), nullable=False),
        sa.Column("is_original_submission", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("public_on_publish", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "version_number", name="uq_manuscript_publication_version"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_manuscript_files_publication_id", "manuscript_files", ["publication_id"], unique=False)
    op.create_index("ix_manuscript_files_author_id", "manuscript_files", ["author_id"], unique=False)
    op.create_index("ix_manuscript_files_sha256", "manuscript_files", ["sha256"], unique=False)
    op.create_index("ix_manuscript_files_uploaded_at", "manuscript_files", ["uploaded_at"], unique=False)

    op.create_table(
        "trust_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", sa.String(length=60), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("manuscript_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("submission_sequence", sa.Integer(), nullable=False),
        sa.Column("publication_version", sa.Integer(), nullable=False),
        sa.Column("fingerprint_sha256", sa.String(length=64), nullable=False),
        sa.Column("snapshot_payload", postgresql.JSONB(), nullable=False),
        sa.Column("certificate_version", sa.String(length=40), nullable=False, server_default="1.0"),
        sa.Column("immutable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manuscript_file_id"], ["manuscript_files.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "submission_sequence", name="uq_trust_snapshot_publication_sequence"),
        sa.UniqueConstraint("submission_id"),
    )
    op.create_index("ix_trust_snapshots_submission_id", "trust_snapshots", ["submission_id"], unique=True)
    op.create_index("ix_trust_snapshots_publication_id", "trust_snapshots", ["publication_id"], unique=False)
    op.create_index("ix_trust_snapshots_author_id", "trust_snapshots", ["author_id"], unique=False)
    op.create_index("ix_trust_snapshots_fingerprint_sha256", "trust_snapshots", ["fingerprint_sha256"], unique=False)
    op.create_index("ix_trust_snapshots_submitted_at", "trust_snapshots", ["submitted_at"], unique=False)

    op.create_table(
        "trust_confidentiality_acceptances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("statement_version", sa.String(length=50), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "user_id", name="uq_trust_confidentiality_publication_user"),
    )
    op.create_index("ix_trust_confidentiality_acceptances_publication_id", "trust_confidentiality_acceptances", ["publication_id"], unique=False)
    op.create_index("ix_trust_confidentiality_acceptances_user_id", "trust_confidentiality_acceptances", ["user_id"], unique=False)

    op.create_table(
        "trust_conflict_declarations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("declared_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_id", "user_id", name="uq_trust_conflict_publication_user"),
    )
    op.create_index("ix_trust_conflict_declarations_publication_id", "trust_conflict_declarations", ["publication_id"], unique=False)
    op.create_index("ix_trust_conflict_declarations_user_id", "trust_conflict_declarations", ["user_id"], unique=False)
    op.create_index("ix_trust_conflict_declarations_decision", "trust_conflict_declarations", ["decision"], unique=False)

    op.create_table(
        "trust_access_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=80), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("object_type", sa.String(length=80), nullable=True),
        sa.Column("object_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("previous_hash", sa.String(length=64), nullable=True),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["publication_id"], ["publications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_hash"),
    )
    op.create_index("ix_trust_access_events_publication_id", "trust_access_events", ["publication_id"], unique=False)
    op.create_index("ix_trust_access_events_actor_user_id", "trust_access_events", ["actor_user_id"], unique=False)
    op.create_index("ix_trust_access_events_action", "trust_access_events", ["action"], unique=False)
    op.create_index("ix_trust_access_events_event_hash", "trust_access_events", ["event_hash"], unique=True)
    op.create_index("ix_trust_access_events_created_at", "trust_access_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("trust_access_events")
    op.drop_table("trust_conflict_declarations")
    op.drop_table("trust_confidentiality_acceptances")
    op.drop_table("trust_snapshots")
    op.drop_table("manuscript_files")
    op.drop_index("ix_publications_submission_method", table_name="publications")
    op.drop_column("publications", "submission_method")

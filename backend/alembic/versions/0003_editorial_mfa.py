"""Editorial MFA and recovery codes.

Revision ID: 0003_editorial_mfa
Revises: 0002_authentication_v2
"""

from alembic import op

import sqlalchemy as sa

from sqlalchemy.dialects import (
    postgresql,
)


revision = "0003_editorial_mfa"

down_revision = (
    "0002_authentication_v2"
)

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "editor_mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "editor_mfa_generation",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "editor_mfa_enabled_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_editor_mfa_enabled",
        "users",
        ["editor_mfa_enabled"],
        unique=False,
    )

    op.create_table(
        "mfa_recovery_codes",

        sa.Column(
            "id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=False,
        ),

        sa.Column(
            "code_hash",
            sa.String(
                length=128
            ),
            nullable=False,
        ),

        sa.Column(
            "used_at",
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

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_mfa_recovery_codes_user_id",
        "mfa_recovery_codes",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_mfa_recovery_codes_code_hash",
        "mfa_recovery_codes",
        ["code_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mfa_recovery_codes_code_hash",
        table_name=(
            "mfa_recovery_codes"
        ),
    )

    op.drop_index(
        "ix_mfa_recovery_codes_user_id",
        table_name=(
            "mfa_recovery_codes"
        ),
    )

    op.drop_table(
        "mfa_recovery_codes"
    )

    op.drop_index(
        "ix_users_editor_mfa_enabled",
        table_name="users",
    )

    op.drop_column(
        "users",
        "editor_mfa_enabled_at",
    )

    op.drop_column(
        "users",
        "editor_mfa_generation",
    )

    op.drop_column(
        "users",
        "editor_mfa_enabled",
    )
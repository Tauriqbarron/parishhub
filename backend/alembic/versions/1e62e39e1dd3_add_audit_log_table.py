"""Add audit log table for tracking data modifications.

Revision ID: 1e62e39e1dd3
Revises: 7b6608946158
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1e62e39e1dd3"
down_revision = "7b6608946158"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("user_email", sa.String(255), nullable=True),
        sa.Column("user_ip", sa.String(45), nullable=True),
        sa.Column("action", sa.String(10), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("old_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_audit_log_id", "audit_log", ["id"], unique=False)
    op.create_index(
        "ix_audit_log_user_email", "audit_log", ["user_email"], unique=False
    )
    op.create_index("ix_audit_log_action", "audit_log", ["action"], unique=False)
    op.create_index(
        "ix_audit_log_resource_type", "audit_log", ["resource_type"], unique=False
    )
    op.create_index(
        "ix_audit_log_resource_id", "audit_log", ["resource_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_resource_id")
    op.drop_index("ix_audit_log_resource_type")
    op.drop_index("ix_audit_log_action")
    op.drop_index("ix_audit_log_user_email")
    op.drop_index("ix_audit_log_id")
    op.drop_table("audit_log")

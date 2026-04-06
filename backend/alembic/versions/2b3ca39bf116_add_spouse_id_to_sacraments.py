"""add spouse_id to sacraments

Revision ID: 2b3ca39bf116
Revises: 88935619158b
"""

from alembic import op
import sqlalchemy as sa

revision = "2b3ca39bf116"
down_revision = "88935619158b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sacraments", sa.Column("spouse_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_sacraments_spouse",
        "sacraments",
        "persons",
        ["spouse_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_sacraments_spouse", "sacraments", type_="foreignkey")
    op.drop_column("sacraments", "spouse_id")

"""add origin_sacrament_id to households

Revision ID: e8f3a5b7c1d4
Revises: d1e2f3a4b5c6
Create Date: 2026-04-05 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8f3a5b7c1d4"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "households", sa.Column("origin_sacrament_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_households_origin_sacrament",
        "households",
        "sacraments",
        ["origin_sacrament_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_households_origin_sacrament", "households", type_="foreignkey"
    )
    op.drop_column("households", "origin_sacrament_id")

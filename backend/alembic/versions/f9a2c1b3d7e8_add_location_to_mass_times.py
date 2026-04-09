"""add location to mass_times

Revision ID: f9a2c1b3d7e8
Revises: 2b3ca39bf116
Create Date: 2026-04-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f9a2c1b3d7e8"
down_revision: Union[str, None] = "2b3ca39bf116"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mass_times",
        sa.Column("location", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mass_times", "location")

"""add attending_since to households

Revision ID: d1e2f3a4b5c6
Revises: c864d36f58b2
Create Date: 2026-03-17 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "c864d36f58b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("households", sa.Column("attending_since", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("households", "attending_since")

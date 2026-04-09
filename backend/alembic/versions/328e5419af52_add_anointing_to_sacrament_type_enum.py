"""add anointing to sacrament_type_enum

Revision ID: 328e5419af52
Revises: a6260a847ea6
Create Date: 2026-03-11 22:03:16.708070

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "328e5419af52"
down_revision: Union[str, None] = "a6260a847ea6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE sacrament_type_enum ADD VALUE IF NOT EXISTS 'ANOINTING'")


def downgrade() -> None:
    pass

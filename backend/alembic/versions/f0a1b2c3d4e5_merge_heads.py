"""merge heads

Revision ID: f0a1b2c3d4e5
Revises: 55af0d940063, d1e2f3a4b5c6
Create Date: 2026-03-17 12:00:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "f0a1b2c3d4e5"
down_revision = ("55af0d940063", "d1e2f3a4b5c6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

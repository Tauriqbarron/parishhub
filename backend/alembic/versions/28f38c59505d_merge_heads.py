"""merge_heads

Revision ID: 28f38c59505d
Revises: e7c8d9a0b1f2, 1e62e39e1dd3
Create Date: 2026-04-07 09:44:59.205332

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "28f38c59505d"
down_revision: Union[str, None] = ("e7c8d9a0b1f2", "1e62e39e1dd3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""add nz_addresses table for LINZ address autocomplete

Revision ID: a1b2c3d4e5f6
Revises: f0a1b2c3d4e5
Create Date: 2026-03-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "nz_addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_address", sa.String(400), nullable=False),
        sa.Column("full_address_ascii", sa.String(250), nullable=True),
        sa.Column("address_number", sa.String(20), nullable=True),
        sa.Column("road_name", sa.String(100), nullable=True),
        sa.Column("road_type_name", sa.String(50), nullable=True),
        sa.Column("suburb_locality", sa.String(100), nullable=True),
        sa.Column("town_city", sa.String(100), nullable=True),
        sa.Column("postcode", sa.String(10), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        "CREATE INDEX idx_nz_addresses_trgm ON nz_addresses "
        "USING gin (full_address_ascii gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_nz_addresses_prefix ON nz_addresses "
        "(full_address_ascii text_pattern_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_nz_addresses_prefix")
    op.execute("DROP INDEX IF EXISTS idx_nz_addresses_trgm")
    op.drop_table("nz_addresses")

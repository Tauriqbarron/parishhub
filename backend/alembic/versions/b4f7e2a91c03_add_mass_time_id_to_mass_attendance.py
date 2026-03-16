"""add_mass_time_id_to_mass_attendance

Revision ID: b4f7e2a91c03
Revises: 63b6669a3360
Create Date: 2026-03-17 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b4f7e2a91c03"
down_revision: Union[str, None] = "63b6669a3360"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add mass_time_id column
    op.add_column(
        "mass_attendance",
        sa.Column("mass_time_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_mass_attendance_mass_time_id",
        "mass_attendance",
        "mass_times",
        ["mass_time_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_mass_attendance_mass_time_id",
        "mass_attendance",
        ["mass_time_id"],
    )

    # Data migration: backfill mass_time_id by matching mass_time string to mass_times.name
    op.execute(
        """
        UPDATE mass_attendance
        SET mass_time_id = mt.id
        FROM mass_times mt
        WHERE mass_attendance.mass_time = mt.name
          AND mass_attendance.mass_time_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_mass_attendance_mass_time_id", table_name="mass_attendance")
    op.drop_constraint(
        "fk_mass_attendance_mass_time_id",
        "mass_attendance",
        type_="foreignkey",
    )
    op.drop_column("mass_attendance", "mass_time_id")

"""Replace sacrament additional_data JSONB column with typed columns.

YAGNI: Replace JSONB with explicit typed columns for known fields.
"""

from alembic import op
import sqlalchemy as sa


revision = "84d53aa9c360"
down_revision = "28f38c59505d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add typed columns
    op.add_column("sacraments", sa.Column("godfather", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("godmother", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("sponsor", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("minister", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("church", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("parish", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("witness1", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("witness2", sa.Text(), nullable=True))
    op.add_column("sacraments", sa.Column("officiant", sa.Text(), nullable=True))

    # Migrate existing data from JSONB into typed columns (if any)
    op.execute(
        """
        UPDATE sacraments
        SET
            godfather = (additional_data->>'godfather'),
            godmother = (additional_data->>'godmother'),
            sponsor = (additional_data->>'sponsor'),
            minister = (additional_data->>'minister'),
            church = (additional_data->>'church'),
            parish = (additional_data->>'parish'),
            witness1 = (additional_data->>'witness1'),
            witness2 = (additional_data->>'witness2'),
            officiant = (additional_data->>'officiant')
        WHERE additional_data IS NOT NULL
        """
    )

    # Drop the JSONB column
    op.drop_column("sacraments", "additional_data")


def downgrade() -> None:
    # Re-add JSONB column
    op.add_column("sacraments", sa.Column("additional_data", sa.JSON(), nullable=True))

    # Migrate data back from typed columns to JSONB
    op.execute(
        """
        UPDATE sacraments
        SET additional_data = json_build_object(
            'godfather', godfather,
            'godmother', godmother,
            'sponsor', sponsor,
            'minister', minister,
            'church', church,
            'parish', parish,
            'witness1', witness1,
            'witness2', witness2,
            'officiant', officiant
        )
        WHERE godfather IS NOT NULL OR godmother IS NOT NULL OR sponsor IS NOT NULL
           OR minister IS NOT NULL OR church IS NOT NULL OR parish IS NOT NULL
           OR witness1 IS NOT NULL OR witness2 IS NOT NULL OR officiant IS NOT NULL
        """
    )

    # Drop typed columns
    op.drop_column("sacraments", "officiant")
    op.drop_column("sacraments", "witness2")
    op.drop_column("sacraments", "witness1")
    op.drop_column("sacraments", "parish")
    op.drop_column("sacraments", "church")
    op.drop_column("sacraments", "minister")
    op.drop_column("sacraments", "sponsor")
    op.drop_column("sacraments", "godmother")
    op.drop_column("sacraments", "godfather")

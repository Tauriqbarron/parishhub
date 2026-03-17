"""remove other from gender enum

Revision ID: 55af0d940063
Revises: c864d36f58b2
Create Date: 2026-03-17 14:29:48.402001

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "55af0d940063"
down_revision: Union[str, None] = "c864d36f58b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, update any existing rows that have 'OTHER' to NULL
    op.execute("UPDATE persons SET gender = NULL WHERE gender = 'OTHER'")

    # Rename the old enum type
    op.execute("ALTER TYPE gender_enum RENAME TO gender_enum_old")

    # Create the new enum type without OTHER
    op.execute("CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE')")

    # Update the column to use the new enum type
    op.execute(
        "ALTER TABLE persons ALTER COLUMN gender TYPE gender_enum "
        "USING gender::text::gender_enum"
    )

    # Drop the old enum type
    op.execute("DROP TYPE gender_enum_old")


def downgrade() -> None:
    # Rename the current enum type
    op.execute("ALTER TYPE gender_enum RENAME TO gender_enum_old")

    # Create the enum type with OTHER
    op.execute("CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE', 'OTHER')")

    # Update the column to use the restored enum type
    op.execute(
        "ALTER TABLE persons ALTER COLUMN gender TYPE gender_enum "
        "USING gender::text::gender_enum"
    )

    # Drop the old enum type
    op.execute("DROP TYPE gender_enum_old")

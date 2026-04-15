"""add_ministries_tables

Revision ID: b7c8d9e0f1a2
Revises: f9a2c1b3d7e8
Create Date: 2026-04-15 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "f9a2c1b3d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- ministries ---
    op.create_table(
        "ministries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("leader_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["leader_id"], ["persons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # --- ministry_members ---
    op.create_table(
        "ministry_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ministry_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="member"),
        sa.Column("joined_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ministry_id"], ["ministries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ministry_id", "person_id", name="uq_ministry_person"),
    )
    op.create_index("ix_ministry_members_ministry_id", "ministry_members", ["ministry_id"])
    op.create_index("ix_ministry_members_person_id", "ministry_members", ["person_id"])

    # --- ministry_events ---
    op.create_table(
        "ministry_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ministry_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ministry_id"], ["ministries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ministry_events_ministry_id", "ministry_events", ["ministry_id"])
    op.create_index("ix_ministry_events_event_date", "ministry_events", ["event_date"])

    # --- ministry_event_attendance ---
    op.create_table(
        "ministry_event_attendance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("attended", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["ministry_events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["person_id"], ["persons.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "person_id", name="uq_event_person"),
    )
    op.create_index(
        "ix_ministry_event_attendance_event_id",
        "ministry_event_attendance",
        ["event_id"],
    )
    op.create_index(
        "ix_ministry_event_attendance_person_id",
        "ministry_event_attendance",
        ["person_id"],
    )

    # --- user_roles ---
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("ministry_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ministry_id"], ["ministries.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_email", "role", "ministry_id", name="uq_user_role_ministry"),
    )
    op.create_index("ix_user_roles_user_email", "user_roles", ["user_email"])
    op.create_index("ix_user_roles_ministry_id", "user_roles", ["ministry_id"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("ix_user_roles_ministry_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_email", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("ix_ministry_event_attendance_person_id", table_name="ministry_event_attendance")
    op.drop_index("ix_ministry_event_attendance_event_id", table_name="ministry_event_attendance")
    op.drop_table("ministry_event_attendance")

    op.drop_index("ix_ministry_events_event_date", table_name="ministry_events")
    op.drop_index("ix_ministry_events_ministry_id", table_name="ministry_events")
    op.drop_table("ministry_events")

    op.drop_index("ix_ministry_members_person_id", table_name="ministry_members")
    op.drop_index("ix_ministry_members_ministry_id", table_name="ministry_members")
    op.drop_table("ministry_members")

    op.drop_table("ministries")

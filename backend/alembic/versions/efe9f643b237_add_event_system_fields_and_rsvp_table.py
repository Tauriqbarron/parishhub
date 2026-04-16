"""add event system fields and rsvp table

Revision ID: efe9f643b237
Revises: b7c8d9e0f1a2
Create Date: 2026-04-17 00:09:50.616856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'efe9f643b237'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to ministry_events
    op.add_column('ministry_events', sa.Column('start_time', sa.String(length=5), nullable=True))
    op.add_column('ministry_events', sa.Column('end_time', sa.String(length=5), nullable=True))
    op.add_column('ministry_events', sa.Column('event_type', sa.String(length=50), nullable=False, server_default='other'))
    op.add_column('ministry_events', sa.Column('capacity', sa.Integer(), nullable=True))
    op.add_column('ministry_events', sa.Column('recurrence_rule', sa.String(length=200), nullable=True))
    op.add_column('ministry_events', sa.Column('recurrence_end', sa.Date(), nullable=True))
    op.add_column('ministry_events', sa.Column('is_cancelled', sa.Boolean(), nullable=False, server_default='false'))

    # Create event_rsvps table
    op.create_table('event_rsvps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['ministry_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'person_id', name='uq_event_rsvp_person')
    )
    op.create_index(op.f('ix_event_rsvps_event_id'), 'event_rsvps', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_rsvps_person_id'), 'event_rsvps', ['person_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_event_rsvps_person_id'), table_name='event_rsvps')
    op.drop_index(op.f('ix_event_rsvps_event_id'), table_name='event_rsvps')
    op.drop_table('event_rsvps')
    op.drop_column('ministry_events', 'is_cancelled')
    op.drop_column('ministry_events', 'recurrence_end')
    op.drop_column('ministry_events', 'recurrence_rule')
    op.drop_column('ministry_events', 'capacity')
    op.drop_column('ministry_events', 'event_type')
    op.drop_column('ministry_events', 'end_time')
    op.drop_column('ministry_events', 'start_time')

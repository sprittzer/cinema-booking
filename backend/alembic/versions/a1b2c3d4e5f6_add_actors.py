"""add actors

Revision ID: a1b2c3d4e5f6
Revises: cb318f38626c
Create Date: 2026-05-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cb318f38626c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'actors',
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('birth_year', sa.Integer(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'movie_actors',
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('character', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('movie_id', 'actor_id'),
    )


def downgrade() -> None:
    op.drop_table('movie_actors')
    op.drop_table('actors')

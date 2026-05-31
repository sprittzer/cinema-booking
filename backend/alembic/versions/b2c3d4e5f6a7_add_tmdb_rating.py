"""add tmdb_rating to movies

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-30
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("tmdb_rating", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("movies", "tmdb_rating")

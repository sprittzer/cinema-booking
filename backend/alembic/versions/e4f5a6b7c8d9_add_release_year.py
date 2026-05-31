"""add release_year to movies

Revision ID: e4f5a6b7c8d9
Revises: b2c3d4e5f6a7
Create Date: 2026-05-30
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("release_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("movies", "release_year")

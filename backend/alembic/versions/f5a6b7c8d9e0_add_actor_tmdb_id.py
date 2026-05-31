"""add tmdb_id to actors

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-05-30
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("actors", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_actor_tmdb_id", "actors", ["tmdb_id"])


def downgrade() -> None:
    op.drop_constraint("uq_actor_tmdb_id", "actors", type_="unique")
    op.drop_column("actors", "tmdb_id")

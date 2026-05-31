"""remove moderator role

Revision ID: g6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-05-31
"""
from typing import Union

from alembic import op

revision: str = "g6b7c8d9e0f1"
down_revision: Union[str, None] = "f5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'USER' WHERE role::text = 'MODERATOR'")


def downgrade() -> None:
    pass

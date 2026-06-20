"""add post announcements

Revision ID: 7c2f93d41a60
Revises: 4b91d2a8c3ef
Create Date: 2026-06-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c2f93d41a60"
down_revision: Union[str, Sequence[str], None] = "4b91d2a8c3ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column(
            "is_announcement",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("posts", "is_announcement")

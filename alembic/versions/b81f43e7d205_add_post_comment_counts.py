"""add post comment counts

Revision ID: b81f43e7d205
Revises: a6d8e14c92b7
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b81f43e7d205"
down_revision: Union[str, Sequence[str], None] = "a6d8e14c92b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("comments_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.execute(
        """
        UPDATE posts
        SET comments_count = (
            SELECT count(*) FROM comments WHERE comments.post_id = posts.id
        )
        """
    )


def downgrade() -> None:
    op.drop_column("posts", "comments_count")

"""add user post likes

Revision ID: a6d8e14c92b7
Revises: 7c2f93d41a60
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6d8e14c92b7"
down_revision: Union[str, Sequence[str], None] = "7c2f93d41a60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "post_id", name="uq_post_likes_user_post"
        ),
    )
    op.create_index(
        op.f("ix_post_likes_post_id"), "post_likes", ["post_id"], unique=False
    )
    op.create_index(
        op.f("ix_post_likes_user_id"), "post_likes", ["user_id"], unique=False
    )
    # Legacy counters have no user identity and therefore cannot be withdrawn.
    op.execute("UPDATE posts SET likes = 0")


def downgrade() -> None:
    op.drop_index(op.f("ix_post_likes_user_id"), table_name="post_likes")
    op.drop_index(op.f("ix_post_likes_post_id"), table_name="post_likes")
    op.drop_table("post_likes")

"""set_review_created_at_default

Revision ID: b6a2f8d9c3e1
Revises: 9b7c2d1a4e8f
Create Date: 2026-05-07 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b6a2f8d9c3e1"
down_revision: Union[str, None] = "9b7c2d1a4e8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE reviews SET created_at = NOW() WHERE created_at IS NULL")
    op.alter_column(
        "reviews",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "reviews",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=True,
    )

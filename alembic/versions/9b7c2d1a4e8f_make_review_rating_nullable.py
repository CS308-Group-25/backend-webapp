"""make_review_rating_nullable

Revision ID: 9b7c2d1a4e8f
Revises: 1ac64de81ea7
Create Date: 2026-05-07 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b7c2d1a4e8f"
down_revision: Union[str, None] = "1ac64de81ea7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "reviews",
        "rating",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("DELETE FROM reviews WHERE rating IS NULL")
    op.alter_column(
        "reviews",
        "rating",
        existing_type=sa.Integer(),
        nullable=False,
    )

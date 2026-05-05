"""add variant_name to cart_items

Revision ID: a3f82c1d9e05
Revises: 4fd413fc07c0
Create Date: 2026-05-02

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f82c1d9e05"
down_revision: Union[str, None] = "4fd413fc07c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable variant_name column to cart_items table
    op.add_column("cart_items", sa.Column("variant_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("cart_items", "variant_name")

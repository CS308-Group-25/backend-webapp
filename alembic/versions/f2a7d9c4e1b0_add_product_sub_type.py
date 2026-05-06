"""add product sub type

Revision ID: f2a7d9c4e1b0
Revises: e372220d47d6
Create Date: 2026-05-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2a7d9c4e1b0"
down_revision: Union[str, None] = "e372220d47d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("sub_type", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("products", "sub_type")

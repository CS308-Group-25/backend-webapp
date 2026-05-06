"""add store_credit to users

Revision ID: 1ac64de81ea7
Revises: d47993e9edec
Create Date: 2026-05-06 14:06:43.575664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1ac64de81ea7'
down_revision: Union[str, None] = 'd47993e9edec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('store_credit', sa.Numeric(precision=10, scale=2), nullable=False, server_default=sa.text("0.00"))
    )


def downgrade() -> None:
    op.drop_column('users', 'store_credit')
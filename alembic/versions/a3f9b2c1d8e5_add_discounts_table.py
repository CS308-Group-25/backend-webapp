"""add discounts table

Revision ID: a3f9b2c1d8e5
Revises: 1e9231e0f50a
Create Date: 2026-05-03 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a3f9b2c1d8e5'
down_revision: Union[str, None] = '1e9231e0f50a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'discounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_ids', sa.JSON(), nullable=False),
        sa.Column('discount_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('original_prices', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(
            timezone=True), 
            server_default=sa.text('now()'), 
            nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_discounts_id'), 'discounts', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_discounts_id'), table_name='discounts')
    op.drop_table('discounts')

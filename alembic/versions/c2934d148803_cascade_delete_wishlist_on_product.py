"""cascade_delete_wishlist_on_product

Revision ID: c2934d148803
Revises: 430b939a1454
Create Date: 2026-06-12 14:10:42.757379

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c2934d148803'
down_revision: Union[str, None] = '430b939a1454'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(op.f('wishlist_items_product_id_fkey'), 'wishlist_items', type_='foreignkey')
    op.create_foreign_key(None, 'wishlist_items', 'products', ['product_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(None, 'wishlist_items', type_='foreignkey')
    op.create_foreign_key(op.f('wishlist_items_product_id_fkey'), 'wishlist_items', 'products', ['product_id'], ['id'])
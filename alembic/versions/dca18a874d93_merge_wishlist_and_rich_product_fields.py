"""merge_wishlist_and_rich_product_fields

Revision ID: dca18a874d93
Revises: 37ecd68a1d1e, 4fd413fc07c0
Create Date: 2026-04-23 22:30:03.940476

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'dca18a874d93'
down_revision: Union[str, None] = ('37ecd68a1d1e', '4fd413fc07c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
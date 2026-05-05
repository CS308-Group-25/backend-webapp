"""merge discounts and variant_name branches

Revision ID: 832e2b6965fb
Revises: a3f9b2c1d8e5, e77703bdd591
Create Date: 2026-05-06 00:08:16.561711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '832e2b6965fb'
down_revision: Union[str, None] = ('a3f9b2c1d8e5', 'e77703bdd591')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
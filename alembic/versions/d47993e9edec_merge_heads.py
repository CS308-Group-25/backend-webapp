"""merge heads

Revision ID: d47993e9edec
Revises: 832e2b6965fb, f2a7d9c4e1b0
Create Date: 2026-05-06 02:17:15.439868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd47993e9edec'
down_revision: Union[str, None] = ('832e2b6965fb', 'f2a7d9c4e1b0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
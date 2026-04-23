"""merge product and cart migrations

Revision ID: 201d3ed16cc1
Revises: ce911e52db70, cff6c066e82f
Create Date: 2026-03-27 02:15:05.411349

"""

from typing import Sequence, Union

import sqlalchemy as sa  # noqa: F401

from alembic import op  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "201d3ed16cc1"
down_revision: Union[str, None] = ("ce911e52db70", "cff6c066e82f")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

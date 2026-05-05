"""merge multiple heads

Revision ID: e372220d47d6
Revises: a3f9b2c1d8e5, e77703bdd591
Create Date: 2026-05-05 21:22:57.566344

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e372220d47d6"
down_revision: Union[str, None] = ("a3f9b2c1d8e5", "e77703bdd591")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

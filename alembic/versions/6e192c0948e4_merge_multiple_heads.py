"""merge multiple heads

Revision ID: 6e192c0948e4
Revises: 1e9231e0f50a, a3f82c1d9e05
Create Date: 2026-05-02 22:00:00.266487

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "6e192c0948e4"
down_revision: Union[str, None] = ("1e9231e0f50a", "a3f82c1d9e05")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

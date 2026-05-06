"""merge multiple heads

Revision ID: e2e260754b17
Revises: 6e192c0948e4
Create Date: 2026-05-02 22:31:09.315470

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e2e260754b17"
down_revision: Union[str, None] = "6e192c0948e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

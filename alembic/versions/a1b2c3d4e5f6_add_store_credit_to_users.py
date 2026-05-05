"""add store_credit column to users table

Revision ID: a1b2c3d4e5f6
Revises: 713595850f32
Create Date: 2026-05-05
"""
import sqlalchemy as sa

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "713595850f32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "store_credit",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0.00",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "store_credit")

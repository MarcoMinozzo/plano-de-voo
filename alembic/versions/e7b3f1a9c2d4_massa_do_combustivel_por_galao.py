"""massa do combustível por galão

Revision ID: e7b3f1a9c2d4
Revises: d4a8c0e21b67
Create Date: 2026-11-24 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7b3f1a9c2d4"
down_revision: Union[str, Sequence[str], None] = "d4a8c0e21b67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("aeronave", sa.Column("combustivel_kg_por_gal", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("aeronave", "combustivel_kg_por_gal")

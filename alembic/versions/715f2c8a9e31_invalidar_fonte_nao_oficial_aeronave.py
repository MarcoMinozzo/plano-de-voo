"""Invalidate aircraft records without an official manual reference.

Revision ID: 715f2c8a9e31
Revises: d4a8c0e21b67
Create Date: 2026-11-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "715f2c8a9e31"
down_revision: Union[str, Sequence[str], None] = "d4a8c0e21b67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE aeronave
            SET manual_estado = 'ausente'
            WHERE manual_estado <> 'ausente'
              AND (
                    fonte_manual IS NULL
                    OR trim(fonte_manual) = ''
                    OR lower(fonte_manual) LIKE '%números de estudo%'
              )
            """
        )
    )


def downgrade() -> None:
    raise RuntimeError(
        "Não é seguro reativar automaticamente registros sem referência oficial verificável."
    )

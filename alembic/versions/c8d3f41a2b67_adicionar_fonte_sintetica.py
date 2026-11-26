"""Adicionar procedência de demonstração sem data editorial.

Revision ID: c8d3f41a2b67
Revises: 9b3d0c2e1f44
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8d3f41a2b67"
down_revision: Union[str, Sequence[str], None] = "9b3d0c2e1f44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("fonte_tecnica_aeronave") as batch_op:
        batch_op.drop_constraint("ck_fonte_tecnica_tipo", type_="check")
        batch_op.create_check_constraint(
            "ck_fonte_tecnica_tipo",
            "tipo_fonte in ('oficial', 'secundaria', 'sintetica')",
        )
        batch_op.alter_column(
            "data_publicacao",
            existing_type=sa.DateTime(timezone=True),
            nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(
        sa.text(
            "SELECT 1 FROM fonte_tecnica_aeronave "
            "WHERE tipo_fonte = 'sintetica' OR data_publicacao IS NULL LIMIT 1"
        )
    ).first():
        raise RuntimeError(
            "Não é seguro remover procedências sintéticas ou registros sem data editorial."
        )
    with op.batch_alter_table("fonte_tecnica_aeronave") as batch_op:
        batch_op.drop_constraint("ck_fonte_tecnica_tipo", type_="check")
        batch_op.create_check_constraint(
            "ck_fonte_tecnica_tipo",
            "tipo_fonte in ('oficial', 'secundaria')",
        )
        batch_op.alter_column(
            "data_publicacao",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )

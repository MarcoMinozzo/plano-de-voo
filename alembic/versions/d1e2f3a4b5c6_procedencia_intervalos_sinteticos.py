"""Adicionar intervalos e método de geração para fontes sintéticas.

Revision ID: d1e2f3a4b5c6
Revises: c8d3f41a2b67
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c8d3f41a2b67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("fonte_tecnica_aeronave") as batch_op:
        batch_op.add_column(sa.Column("limite_inferior", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("limite_superior", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("metodo_geracao", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("versao_semente", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("incerteza", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("justificativa_comparabilidade", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(
        sa.text(
            "SELECT 1 FROM fonte_tecnica_aeronave "
            "WHERE tipo_fonte = 'sintetica' "
            "AND (limite_inferior IS NOT NULL OR limite_superior IS NOT NULL "
            "OR metodo_geracao IS NOT NULL OR versao_semente IS NOT NULL "
            "OR incerteza IS NOT NULL OR justificativa_comparabilidade IS NOT NULL) "
            "LIMIT 1"
        )
    ).first():
        raise RuntimeError(
            "Não é seguro remover metadados de faixas e geração sintética."
        )
    with op.batch_alter_table("fonte_tecnica_aeronave") as batch_op:
        batch_op.drop_column("justificativa_comparabilidade")
        batch_op.drop_column("incerteza")
        batch_op.drop_column("versao_semente")
        batch_op.drop_column("metodo_geracao")
        batch_op.drop_column("limite_superior")
        batch_op.drop_column("limite_inferior")

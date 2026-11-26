"""Adicionar procedência técnica por campo.

Revision ID: 9b3d0c2e1f44
Revises: 715f2c8a9e31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b3d0c2e1f44"
down_revision: Union[str, Sequence[str], None] = "715f2c8a9e31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fonte_tecnica_aeronave",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aeronave_id", sa.Integer(), nullable=False),
        sa.Column("campo", sa.String(length=80), nullable=False),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("unidade", sa.String(length=20), nullable=False),
        sa.Column("tipo_fonte", sa.String(length=20), nullable=False),
        sa.Column("publicador", sa.String(length=200), nullable=False),
        sa.Column("referencia", sa.Text(), nullable=False),
        sa.Column("data_publicacao", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_consulta", sa.DateTime(timezone=True), nullable=False),
        sa.Column("modelo_variante", sa.String(length=200), nullable=False),
        sa.Column("perfil", sa.String(length=200), nullable=True),
        sa.Column("revisao_edicao", sa.String(length=200), nullable=True),
        sa.Column("pagina_tabela", sa.String(length=200), nullable=True),
        sa.Column("selecionada", sa.Boolean(), nullable=False),
        sa.Column("divergencia", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["aeronave_id"], ["aeronave.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tipo_fonte in ('oficial', 'secundaria')", name="ck_fonte_tecnica_tipo"),
    )
    op.create_index(
        "ix_fonte_tecnica_aeronave_aeronave_id",
        "fonte_tecnica_aeronave",
        ["aeronave_id"],
    )
    op.execute(
        sa.text(
            "UPDATE aeronave SET manual_estado = 'ausente' "
            "WHERE manual_estado = 'gravado' "
            "AND NOT EXISTS ("
            "SELECT 1 FROM fonte_tecnica_aeronave f "
            "WHERE f.aeronave_id = aeronave.id AND f.selecionada = true"
            ")"
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fonte_tecnica_aeronave_aeronave_id",
        table_name="fonte_tecnica_aeronave",
    )
    op.drop_table("fonte_tecnica_aeronave")

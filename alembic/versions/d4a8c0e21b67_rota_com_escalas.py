"""rota com escalas

Revision ID: d4a8c0e21b67
Revises: c58b11f057c2
Create Date: 2026-11-12 07:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4a8c0e21b67"
down_revision: Union[str, Sequence[str], None] = "c58b11f057c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emenda_rotaer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo_emenda", sa.String(length=80), nullable=False),
        sa.Column("vigente", sa.Boolean(), nullable=False),
        sa.Column("carregada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_emenda_rotaer_uma_vigente",
        "emenda_rotaer",
        ["vigente"],
        unique=True,
        postgresql_where=sa.text("vigente"),
    )
    op.create_table(
        "extrato_rab",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("referencia", sa.String(length=160), nullable=False),
        sa.Column("carregado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint("ck_aerodromo_icao_quatro", "aerodromo", type_="check")
    op.alter_column("aerodromo", "icao", existing_type=sa.String(length=4), type_=sa.String(length=16))
    op.alter_column(
        "plano_de_voo",
        "origem_icao",
        existing_type=sa.String(length=4),
        type_=sa.String(length=16),
    )
    op.alter_column(
        "plano_de_voo",
        "destino_icao",
        existing_type=sa.String(length=4),
        type_=sa.String(length=16),
    )
    op.add_column(
        "aerodromo",
        sa.Column("tipo", sa.String(length=20), nullable=False, server_default="aerodromo"),
    )
    op.add_column("aerodromo", sa.Column("emenda_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_aerodromo_emenda", "aerodromo", "emenda_rotaer", ["emenda_id"], ["id"])
    op.alter_column("aeronave", "nome", existing_type=sa.String(length=120), type_=sa.String(length=200))
    op.add_column("aeronave", sa.Column("frota", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "aeronave",
        sa.Column("manual_estado", sa.String(length=20), nullable=False, server_default="gravado"),
    )
    op.add_column("aeronave", sa.Column("extrato_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_aeronave_extrato", "aeronave", "extrato_rab", ["extrato_id"], ["id"])
    for coluna, tipo in (
        ("fonte_manual", sa.Text()),
        ("peso_vazio_kg", sa.Float()),
        ("peso_max_decolagem_kg", sa.Float()),
        ("bagagem_max_kg", sa.Float()),
        ("braco_bagagem_m", sa.Float()),
        ("combustivel_valor", sa.Float()),
        ("combustivel_unidade", sa.String(length=20)),
        ("velocidade_valor", sa.Float()),
        ("velocidade_unidade", sa.String(length=20)),
        ("consumo_valor", sa.Float()),
        ("consumo_unidade", sa.String(length=20)),
    ):
        op.alter_column("aeronave", coluna, existing_type=tipo, nullable=True)
    op.add_column(
        "plano_de_voo",
        sa.Column("rota_estado", sa.String(length=20), nullable=False, server_default="aceitavel"),
    )
    op.add_column("plano_de_voo", sa.Column("motivo", sa.Text(), nullable=True))
    op.add_column("plano_de_voo", sa.Column("hipotese_reabastecimento", sa.Text(), nullable=True))
    op.create_table(
        "trecho",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plano_id", sa.Integer(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("origem_icao", sa.String(length=16), nullable=False),
        sa.Column("destino_icao", sa.String(length=16), nullable=False),
        sa.Column("distancia_valor", sa.Float(), nullable=False),
        sa.Column("distancia_unidade", sa.String(length=20), nullable=False),
        sa.Column("distancia_fonte", sa.Text(), nullable=False),
        sa.Column("proa_valor", sa.Float(), nullable=False),
        sa.Column("proa_unidade", sa.String(length=20), nullable=False),
        sa.Column("proa_fonte", sa.Text(), nullable=False),
        sa.Column("tempo_valor", sa.Float(), nullable=False),
        sa.Column("tempo_unidade", sa.String(length=20), nullable=False),
        sa.Column("tempo_fonte", sa.Text(), nullable=False),
        sa.Column("combustivel_valor", sa.Float(), nullable=False),
        sa.Column("combustivel_unidade", sa.String(length=20), nullable=False),
        sa.Column("combustivel_fonte", sa.Text(), nullable=False),
        sa.Column("vento_estado", sa.String(length=20), nullable=False),
        sa.Column("por_do_sol_estado", sa.String(length=20), nullable=False),
        sa.Column("velocidade_solo_kt", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["destino_icao"], ["aerodromo.icao"]),
        sa.ForeignKeyConstraint(["origem_icao"], ["aerodromo.icao"]),
        sa.ForeignKeyConstraint(["plano_id"], ["plano_de_voo.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trecho_plano_id", "trecho", ["plano_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trecho_plano_id", table_name="trecho")
    op.drop_table("trecho")
    op.drop_column("plano_de_voo", "hipotese_reabastecimento")
    op.drop_column("plano_de_voo", "motivo")
    op.drop_column("plano_de_voo", "rota_estado")
    for coluna, tipo in (
        ("consumo_unidade", sa.String(length=20)),
        ("consumo_valor", sa.Float()),
        ("velocidade_unidade", sa.String(length=20)),
        ("velocidade_valor", sa.Float()),
        ("combustivel_unidade", sa.String(length=20)),
        ("combustivel_valor", sa.Float()),
        ("braco_bagagem_m", sa.Float()),
        ("bagagem_max_kg", sa.Float()),
        ("peso_max_decolagem_kg", sa.Float()),
        ("peso_vazio_kg", sa.Float()),
        ("fonte_manual", sa.Text()),
    ):
        op.alter_column("aeronave", coluna, existing_type=tipo, nullable=False)
    op.drop_constraint("fk_aeronave_extrato", "aeronave", type_="foreignkey")
    op.drop_column("aeronave", "extrato_id")
    op.drop_column("aeronave", "manual_estado")
    op.drop_column("aeronave", "frota")
    op.alter_column("aeronave", "nome", existing_type=sa.String(length=200), type_=sa.String(length=120))
    op.drop_constraint("fk_aerodromo_emenda", "aerodromo", type_="foreignkey")
    op.drop_column("aerodromo", "emenda_id")
    op.drop_column("aerodromo", "tipo")
    op.alter_column(
        "plano_de_voo",
        "destino_icao",
        existing_type=sa.String(length=16),
        type_=sa.String(length=4),
    )
    op.alter_column(
        "plano_de_voo",
        "origem_icao",
        existing_type=sa.String(length=16),
        type_=sa.String(length=4),
    )
    op.alter_column("aerodromo", "icao", existing_type=sa.String(length=16), type_=sa.String(length=4))
    op.create_check_constraint("ck_aerodromo_icao_quatro", "aerodromo", "char_length(icao) = 4")
    op.drop_table("extrato_rab")
    op.drop_index("uq_emenda_rotaer_uma_vigente", table_name="emenda_rotaer")
    op.drop_table("emenda_rotaer")

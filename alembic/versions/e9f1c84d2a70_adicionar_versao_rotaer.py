"""Adicionar proveniência por versão AISWEB ao aeródromo."""

from alembic import op
import sqlalchemy as sa


revision = "e9f1c84d2a70"
down_revision = "a4f3c8d1926e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("aerodromo") as batch_op:
        batch_op.add_column(sa.Column("rotaer_versao_id", sa.String(80), nullable=True))
        batch_op.add_column(sa.Column("rotaer_atualizado_em", sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table("aerodromo") as batch_op:
        batch_op.drop_column("rotaer_atualizado_em")
        batch_op.drop_column("rotaer_versao_id")

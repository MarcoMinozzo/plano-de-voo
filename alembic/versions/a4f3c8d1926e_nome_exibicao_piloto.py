"""Adicionar nome de exibição ao piloto."""

from alembic import op
import sqlalchemy as sa


revision = "a4f3c8d1926e"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("piloto") as batch_op:
        batch_op.add_column(sa.Column("nome_exibicao", sa.String(160), nullable=True))

    op.execute(
        sa.text(
            "UPDATE piloto SET nome_exibicao = identificacao "
            "WHERE nome_exibicao IS NULL"
        )
    )

    with op.batch_alter_table("piloto") as batch_op:
        batch_op.alter_column(
            "nome_exibicao",
            existing_type=sa.String(160),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("piloto") as batch_op:
        batch_op.drop_column("nome_exibicao")

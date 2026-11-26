"""Adicionar contatos ROTAER ao aeródromo."""

from alembic import op
import sqlalchemy as sa


revision = "a7c9e2f4b6d1"
down_revision = "e9f1c84d2a70"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("aerodromo") as batch_op:
        batch_op.add_column(sa.Column("telefone", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("email", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "contatos_rotaer_verificados",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            )
        )


def downgrade():
    with op.batch_alter_table("aerodromo") as batch_op:
        batch_op.drop_column("contatos_rotaer_verificados")
        batch_op.drop_column("email")
        batch_op.drop_column("telefone")

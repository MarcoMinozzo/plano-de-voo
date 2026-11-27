"""Componente de vento de proa ou de cauda em cada trecho."""

from alembic import op
import sqlalchemy as sa


revision = "b8e1a2c3d4f5"
down_revision = "a7c9e2f4b6d1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("trecho") as batch_op:
        batch_op.add_column(sa.Column("vento_sentido", sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column("vento_componente_kt", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("vento_fonte", sa.String(length=80), nullable=True))


def downgrade():
    with op.batch_alter_table("trecho") as batch_op:
        batch_op.drop_column("vento_fonte")
        batch_op.drop_column("vento_componente_kt")
        batch_op.drop_column("vento_sentido")

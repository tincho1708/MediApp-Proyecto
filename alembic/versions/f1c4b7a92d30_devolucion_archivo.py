"""devolucion_archivo

Revision ID: f1c4b7a92d30
Revises: d2a7c9e4f6b1
Create Date: 2026-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1c4b7a92d30'
down_revision: Union[str, Sequence[str], None] = 'd2a7c9e4f6b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('devoluciones', 'contenido', existing_type=sa.Text(), nullable=True)
    op.add_column('devoluciones', sa.Column('archivo_nombre', sa.String(length=255), nullable=True))
    op.add_column('devoluciones', sa.Column('archivo_tipo', sa.String(length=100), nullable=True))
    op.add_column('devoluciones', sa.Column('archivo_datos', sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column('devoluciones', 'archivo_datos')
    op.drop_column('devoluciones', 'archivo_tipo')
    op.drop_column('devoluciones', 'archivo_nombre')
    op.execute("UPDATE devoluciones SET contenido = '' WHERE contenido IS NULL")
    op.alter_column('devoluciones', 'contenido', existing_type=sa.Text(), nullable=False)

"""datos_personales

Revision ID: c9e1f4a2b7d3
Revises: b4d8e2f6a1c9
Create Date: 2026-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9e1f4a2b7d3'
down_revision: Union[str, Sequence[str], None] = 'b4d8e2f6a1c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('medicos', sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
    op.add_column('pacientes', sa.Column('direccion', sa.String(length=255), nullable=True))
    op.add_column('pacientes', sa.Column('ciudad', sa.String(length=100), nullable=True))
    op.add_column('pacientes', sa.Column('codigo_postal', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('pacientes', 'codigo_postal')
    op.drop_column('pacientes', 'ciudad')
    op.drop_column('pacientes', 'direccion')
    op.drop_column('medicos', 'fecha_nacimiento')

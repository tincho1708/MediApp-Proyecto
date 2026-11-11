"""foto_perfil

Revision ID: d5a8b3c1e7f2
Revises: c9e1f4a2b7d3
Create Date: 2026-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd5a8b3c1e7f2'
down_revision: Union[str, Sequence[str], None] = 'c9e1f4a2b7d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for tabla in ('medicos', 'pacientes'):
        op.add_column(tabla, sa.Column('foto_clave', sa.String(length=32), nullable=True))
        op.add_column(tabla, sa.Column('foto_tipo', sa.String(length=50), nullable=True))
        op.add_column(tabla, sa.Column('foto_datos', sa.LargeBinary(), nullable=True))
        op.create_unique_constraint(f'uq_{tabla}_foto_clave', tabla, ['foto_clave'])


def downgrade() -> None:
    for tabla in ('medicos', 'pacientes'):
        op.drop_constraint(f'uq_{tabla}_foto_clave', tabla, type_='unique')
        op.drop_column(tabla, 'foto_datos')
        op.drop_column(tabla, 'foto_tipo')
        op.drop_column(tabla, 'foto_clave')

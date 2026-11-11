"""configuracion_turnos

Revision ID: a7e3c1d9b2f4
Revises: f1c4b7a92d30
Create Date: 2026-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7e3c1d9b2f4'
down_revision: Union[str, Sequence[str], None] = 'f1c4b7a92d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('medicos', sa.Column('duracion_turno', sa.Integer(), nullable=False, server_default='60'))
    op.add_column('medicos', sa.Column('margen_turno', sa.Integer(), nullable=False, server_default='0'))
    op.create_table(
        'fecha_bloqueada',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_medico', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['id_medico'], ['medicos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_fecha_bloqueada_id'), 'fecha_bloqueada', ['id'], unique=False)
    op.create_index(op.f('ix_fecha_bloqueada_id_medico'), 'fecha_bloqueada', ['id_medico'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_fecha_bloqueada_id_medico'), table_name='fecha_bloqueada')
    op.drop_index(op.f('ix_fecha_bloqueada_id'), table_name='fecha_bloqueada')
    op.drop_table('fecha_bloqueada')
    op.drop_column('medicos', 'margen_turno')
    op.drop_column('medicos', 'duracion_turno')

"""devoluciones

Revision ID: c7e2a94f1b08
Revises: a3f9d12c8e45
Create Date: 2026-10-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c7e2a94f1b08'
down_revision: Union[str, Sequence[str], None] = 'a3f9d12c8e45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'devoluciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_medico', sa.Integer(), nullable=False),
        sa.Column('id_paciente', sa.Integer(), nullable=False),
        sa.Column('id_turno', sa.Integer(), nullable=True),
        sa.Column('contenido', sa.Text(), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.Column('leida', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['id_medico'], ['medicos.id']),
        sa.ForeignKeyConstraint(['id_paciente'], ['pacientes.id']),
        sa.ForeignKeyConstraint(['id_turno'], ['turno.id_turno']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_devoluciones_id'), 'devoluciones', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_devoluciones_id'), table_name='devoluciones')
    op.drop_table('devoluciones')

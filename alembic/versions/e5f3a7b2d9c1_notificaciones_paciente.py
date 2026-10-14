"""notificaciones_paciente

Revision ID: e5f3a7b2d9c1
Revises: c7e2a94f1b08
Create Date: 2026-10-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f3a7b2d9c1'
down_revision: Union[str, Sequence[str], None] = 'c7e2a94f1b08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notificaciones_paciente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_paciente', sa.Integer(), nullable=False),
        sa.Column('id_turno', sa.Integer(), nullable=False),
        sa.Column('mensaje', sa.String(length=500), nullable=False),
        sa.Column('leida', sa.Boolean(), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_paciente'], ['pacientes.id']),
        sa.ForeignKeyConstraint(['id_turno'], ['turno.id_turno']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notificaciones_paciente_id'), 'notificaciones_paciente', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notificaciones_paciente_id'), table_name='notificaciones_paciente')
    op.drop_table('notificaciones_paciente')

"""medico_especialidades_m2m

Revision ID: 1ace34242395
Revises: 380ac103be08
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1ace34242395'
down_revision: Union[str, Sequence[str], None] = '380ac103be08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'medico_especialidad',
        sa.Column('id_medico', sa.Integer(), nullable=False),
        sa.Column('id_especialidad', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_medico'], ['medicos.id']),
        sa.ForeignKeyConstraint(['id_especialidad'], ['especialidad.id_especialidad']),
        sa.PrimaryKeyConstraint('id_medico', 'id_especialidad'),
    )
    op.execute(
        "INSERT INTO medico_especialidad (id_medico, id_especialidad) "
        "SELECT id, especialidad_id FROM medicos WHERE especialidad_id IS NOT NULL"
    )
    op.add_column('medicos', sa.Column('setup_token', sa.String(length=255), nullable=True))
    op.drop_column('medicos', 'especialidad_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('medicos', sa.Column('especialidad_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE medicos SET especialidad_id = sub.id_especialidad "
        "FROM (SELECT DISTINCT ON (id_medico) id_medico, id_especialidad FROM medico_especialidad) sub "
        "WHERE medicos.id = sub.id_medico"
    )
    op.drop_column('medicos', 'setup_token')
    op.drop_table('medico_especialidad')

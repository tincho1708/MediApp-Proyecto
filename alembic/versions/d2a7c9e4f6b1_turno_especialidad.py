"""turno_especialidad

Revision ID: d2a7c9e4f6b1
Revises: b8d4e6f1a2c3
Create Date: 2026-10-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2a7c9e4f6b1'
down_revision: Union[str, Sequence[str], None] = 'b8d4e6f1a2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('turno', sa.Column('id_especialidad', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_turno_especialidad', 'turno', 'especialidad', ['id_especialidad'], ['id_especialidad'])
    op.execute("""
        UPDATE turno
        SET id_especialidad = me.id_especialidad
        FROM medico_especialidad me
        WHERE me.id_medico = turno.id_medicos
          AND turno.id_especialidad IS NULL
          AND (SELECT COUNT(*) FROM medico_especialidad m2 WHERE m2.id_medico = turno.id_medicos) = 1
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_turno_especialidad', 'turno', type_='foreignkey')
    op.drop_column('turno', 'id_especialidad')

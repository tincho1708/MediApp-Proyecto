"""turno_duracion

Revision ID: b4d8e2f6a1c9
Revises: a7e3c1d9b2f4
Create Date: 2026-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4d8e2f6a1c9'
down_revision: Union[str, Sequence[str], None] = 'a7e3c1d9b2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('turno', sa.Column('duracion', sa.Integer(), nullable=False, server_default='60'))
    op.execute("""
        UPDATE turno
        SET duracion = medicos.duracion_turno
        FROM medicos
        WHERE medicos.id = turno.id_medicos
    """)


def downgrade() -> None:
    op.drop_column('turno', 'duracion')

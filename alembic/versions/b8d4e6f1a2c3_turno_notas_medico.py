"""turno_notas_medico

Revision ID: b8d4e6f1a2c3
Revises: e5f3a7b2d9c1
Create Date: 2026-10-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8d4e6f1a2c3'
down_revision: Union[str, Sequence[str], None] = 'e5f3a7b2d9c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('turno', sa.Column('notas_medico', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('turno', 'notas_medico')

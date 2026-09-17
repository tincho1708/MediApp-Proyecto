"""google_auth_fields

Revision ID: 0c77135e95c7
Revises: 00a2cf052728
Create Date: 2026-06-05 11:58:24.566378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0c77135e95c7'
down_revision: Union[str, Sequence[str], None] = '00a2cf052728'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('medicos', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('medicos', sa.Column('pin_verificacion', sa.String(length=6), nullable=True))
    op.add_column('medicos', sa.Column('pin_expires', sa.DateTime(), nullable=True))
    op.alter_column('medicos', 'dni',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('medicos', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.create_unique_constraint(None, 'medicos', ['google_id'])
    op.add_column('pacientes', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('pacientes', sa.Column('pin_verificacion', sa.String(length=6), nullable=True))
    op.add_column('pacientes', sa.Column('pin_expires', sa.DateTime(), nullable=True))
    op.alter_column('pacientes', 'dni',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('pacientes', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.create_unique_constraint(None, 'pacientes', ['google_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'pacientes', type_='unique')
    op.alter_column('pacientes', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('pacientes', 'dni',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.drop_column('pacientes', 'pin_expires')
    op.drop_column('pacientes', 'pin_verificacion')
    op.drop_column('pacientes', 'google_id')
    op.drop_constraint(None, 'medicos', type_='unique')
    op.alter_column('medicos', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('medicos', 'dni',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.drop_column('medicos', 'pin_expires')
    op.drop_column('medicos', 'pin_verificacion')
    op.drop_column('medicos', 'google_id')

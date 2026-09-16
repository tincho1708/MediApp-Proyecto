"""medibot_tablas

Revision ID: a3f9d12c8e45
Revises: 1ace34242395
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f9d12c8e45'
down_revision: Union[str, Sequence[str], None] = '1ace34242395'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conversacion_medibot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo_usuario', sa.String(length=20), nullable=False),
        sa.Column('titulo', sa.String(length=120), nullable=False, server_default='Nueva conversación'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text("(NOW() AT TIME ZONE 'utc')")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_conversacion_medibot_usuario', 'conversacion_medibot', ['usuario_id', 'tipo_usuario'])
    op.create_index(op.f('ix_conversacion_medibot_id'), 'conversacion_medibot', ['id'], unique=False)

    op.create_table(
        'mensaje_medibot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_conversacion', sa.Integer(), nullable=False),
        sa.Column('rol', sa.String(length=20), nullable=False),
        sa.Column('contenido', sa.Text(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text("(NOW() AT TIME ZONE 'utc')")),
        sa.ForeignKeyConstraint(['id_conversacion'], ['conversacion_medibot.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_mensaje_medibot_conversacion', 'mensaje_medibot', ['id_conversacion', 'creado_en'])
    op.create_index(op.f('ix_mensaje_medibot_id'), 'mensaje_medibot', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_mensaje_medibot_conversacion', table_name='mensaje_medibot')
    op.drop_index(op.f('ix_mensaje_medibot_id'), table_name='mensaje_medibot')
    op.drop_table('mensaje_medibot')
    op.drop_index('ix_conversacion_medibot_usuario', table_name='conversacion_medibot')
    op.drop_index(op.f('ix_conversacion_medibot_id'), table_name='conversacion_medibot')
    op.drop_table('conversacion_medibot')

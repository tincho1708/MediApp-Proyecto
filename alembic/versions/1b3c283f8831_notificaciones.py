"""notificaciones

Revision ID: 1b3c283f8831
Revises: df94d030364d
Create Date: 2026-08-14 12:06:52.708810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b3c283f8831'
down_revision: Union[str, Sequence[str], None] = 'df94d030364d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('notificaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_medico', sa.Integer(), nullable=False),
    sa.Column('id_turno', sa.Integer(), nullable=False),
    sa.Column('mensaje', sa.String(length=500), nullable=False),
    sa.Column('leida', sa.Boolean(), nullable=True),
    sa.Column('fecha', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_medico'], ['medicos.id'], ),
    sa.ForeignKeyConstraint(['id_turno'], ['turno.id_turno'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notificaciones_id'), 'notificaciones', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notificaciones_id'), table_name='notificaciones')
    op.drop_table('notificaciones')

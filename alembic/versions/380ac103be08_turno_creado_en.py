"""turno_creado_en

Revision ID: 380ac103be08
Revises: 1b3c283f8831
Create Date: 2026-08-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '380ac103be08'
down_revision: Union[str, Sequence[str], None] = '1b3c283f8831'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('turno', sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.alter_column('turno', 'creado_en', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('turno', 'creado_en')

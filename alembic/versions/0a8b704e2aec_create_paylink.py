"""create paylink

Revision ID: 0a8b704e2aec
Revises: 24963e5577b3
Create Date: 2023-07-27 15:08:40.515627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a8b704e2aec'
down_revision = '24963e5577b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'paylink',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True, unique=True),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('is_payed', sa.Boolean(), nullable=False, default=False),
        sa.Column('amount', sa.Float(), nullable=False),
    )


def downgrade() -> None:
    pass

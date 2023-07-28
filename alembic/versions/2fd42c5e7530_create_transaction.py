"""create transaction

Revision ID: 2fd42c5e7530
Revises: 0a8b704e2aec
Create Date: 2023-07-27 15:26:44.318524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fd42c5e7530'
down_revision = '0a8b704e2aec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'transaction',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True, unique=True),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('asset', sa.String(length=10), nullable=False),
        sa.Column('network', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(length=100), nullable=False),
        sa.Column('address', sa.String(length=100), nullable=False),
        sa.Column('paylink_id', sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    pass

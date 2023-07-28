"""create user table

Revision ID: 24963e5577b3
Revises: 
Create Date: 2023-07-27 14:31:58.928882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24963e5577b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('chat_id', sa.BigInteger(), primary_key=True, autoincrement=False, unique=True),
        sa.Column('balance', sa.Float(), nullable=False, default=0.0),
    )


def downgrade() -> None:
    pass

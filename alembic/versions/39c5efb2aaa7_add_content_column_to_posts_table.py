"""add content column to posts table

Revision ID: 39c5efb2aaa7
Revises: 5a69bac1b537
Create Date: 2023-01-27 12:04:45.470239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39c5efb2aaa7'
down_revision = '5a69bac1b537'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass

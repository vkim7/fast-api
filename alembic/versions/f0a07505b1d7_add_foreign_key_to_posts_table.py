"""add foreign key to posts table

Revision ID: f0a07505b1d7
Revises: 4b2734ebdaad
Create Date: 2023-01-28 15:35:10.373060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0a07505b1d7'
down_revision = '4b2734ebdaad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',
                  sa.Column('user_id', sa.Integer(), nullable=False)
                  )
    op.create_foreign_key('post_users_fkey',
                          source_table='posts', referent_table='users',
                          local_cols=['user_id'], remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint(constraint_name='post_users_fkey', table_name='posts')
    op.drop_column(table_name='posts', column_name='user_id')
    pass

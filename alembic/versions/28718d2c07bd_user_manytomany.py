"""user manytomany

Revision ID: 28718d2c07bd
Revises: da314c11d9e9
Create Date: 2021-08-30 17:56:17.616707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28718d2c07bd'
down_revision = 'da314c11d9e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_user_to_group',
    sa.Column('auth_user_id', sa.Integer(), nullable=True),
    sa.Column('auth_user_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['auth_user_group_id'], ['auth_user_group.id'], ),
    sa.ForeignKeyConstraint(['auth_user_id'], ['auth_user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('auth_user_to_group')
    # ### end Alembic commands ###

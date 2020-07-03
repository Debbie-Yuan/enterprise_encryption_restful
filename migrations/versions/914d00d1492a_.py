"""empty message

Revision ID: 914d00d1492a
Revises: 
Create Date: 2020-07-01 23:19:51.549022

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '914d00d1492a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('_password', sa.String(length=128), nullable=False),
    sa.Column('is_delete', sa.Boolean(), nullable=False),
    sa.Column('extension', sa.Integer(), nullable=True),
    sa.Column('permission', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(length=2), nullable=True),
    sa.Column('is_super', sa.Boolean(), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=True),
    sa.Column('e_mail', sa.String(length=128), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
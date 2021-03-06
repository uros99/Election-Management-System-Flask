"""Initial migrate

Revision ID: 5978ed033dab
Revises: 
Create Date: 2021-06-23 15:35:31.770882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5978ed033dab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=45), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=45), nullable=False),
    sa.Column('password', sa.String(length=45), nullable=False),
    sa.Column('forename', sa.String(length=45), nullable=False),
    sa.Column('lastname', sa.String(length=45), nullable=False),
    sa.Column('jmbg', sa.String(length=13), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('jmbg')
    )
    op.create_table('userrole',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('roleId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['roleId'], ['role.id'], ),
    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userrole')
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###

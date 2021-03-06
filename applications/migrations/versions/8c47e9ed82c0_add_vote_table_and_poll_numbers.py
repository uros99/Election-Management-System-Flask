"""Add vote table and poll numbers

Revision ID: 8c47e9ed82c0
Revises: 8901d961d1d9
Create Date: 2021-06-25 20:23:16.229606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c47e9ed82c0'
down_revision = '8901d961d1d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('guid', sa.Integer(), nullable=False),
    sa.Column('pollNumber', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=256), nullable=True),
    sa.Column('electionID', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['electionID'], ['election.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('participant', sa.Column('pollNumber', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'participantelection', 'participant', ['participantId'], ['id'])
    op.create_foreign_key(None, 'participantelection', 'election', ['electionId'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'participantelection', type_='foreignkey')
    op.drop_constraint(None, 'participantelection', type_='foreignkey')
    op.drop_column('participant', 'pollNumber')
    op.drop_table('vote')
    # ### end Alembic commands ###

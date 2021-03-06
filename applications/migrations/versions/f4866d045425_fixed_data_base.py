"""Fixed data base

Revision ID: f4866d045425
Revises: 8c47e9ed82c0
Create Date: 2021-06-28 22:53:32.727554

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f4866d045425'
down_revision = '8c47e9ed82c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pollNumber', sa.Integer(), nullable=True),
    sa.Column('result', sa.Integer(), nullable=True),
    sa.Column('participantID', sa.Integer(), nullable=False),
    sa.Column('electionID', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['electionID'], ['election.id'], ),
    sa.ForeignKeyConstraint(['participantID'], ['participant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('participant', 'pollNumber')
    op.add_column('participantelection', sa.Column('pollNumber', sa.Integer(), nullable=True))
    op.add_column('vote', sa.Column('electionOfficialJmbg', sa.String(length=13), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vote', 'electionOfficialJmbg')
    op.drop_column('participantelection', 'pollNumber')
    op.add_column('participant', sa.Column('pollNumber', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_table('result')
    # ### end Alembic commands ###

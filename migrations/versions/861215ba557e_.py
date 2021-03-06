"""empty message

Revision ID: 861215ba557e
Revises: 
Create Date: 2019-06-09 14:58:06.518857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '861215ba557e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('text_en', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('answer_en', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_member',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('game_id', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_ready', sa.Boolean(), nullable=False),
    sa.Column('resigned_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('game_id', 'user_id', name='unique_game_id_user_id')
    )
    op.create_table('game_question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.String(length=50), nullable=False),
    sa.Column('question_id', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_member_position',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('game_member_id', sa.String(length=50), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_member_id'], ['game_member.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_placement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.String(length=50), nullable=False),
    sa.Column('member_id', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['game_member.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('game_id', 'member_id', name='unique_game_id_member_id')
    )
    op.create_table('game_member_question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.String(length=50), nullable=False),
    sa.Column('game_question_id', sa.Integer(), nullable=False),
    sa.Column('position_id', sa.String(length=50), nullable=True),
    sa.Column('answered_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_question_id'], ['game_question.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['game_member.id'], ),
    sa.ForeignKeyConstraint(['position_id'], ['game_member_position.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('member_id', 'game_question_id', name='unique_member_id_game_question_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game_member_question')
    op.drop_table('game_placement')
    op.drop_table('game_member_position')
    op.drop_table('game_question')
    op.drop_table('game_member')
    op.drop_table('question')
    op.drop_table('game')
    # ### end Alembic commands ###

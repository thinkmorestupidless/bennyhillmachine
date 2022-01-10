"""empty message

Revision ID: 9d71a28fa768
Revises: None
Create Date: 2022-01-09 14:31:38.841438

"""

# revision identifiers, used by Alembic.
revision = '9d71a28fa768'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('converted_videos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('youtube_url', sa.String(), nullable=True),
    sa.Column('converted_url', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('converted_videos')
    # ### end Alembic commands ###

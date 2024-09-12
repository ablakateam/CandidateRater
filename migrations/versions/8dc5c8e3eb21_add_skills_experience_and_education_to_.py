"""Add skills, experience, and education to Candidate model

Revision ID: 8dc5c8e3eb21
Revises: 
Create Date: 2024-09-12 15:25:31.564200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8dc5c8e3eb21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skills', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('experience', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('education', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.drop_column('education')
        batch_op.drop_column('experience')
        batch_op.drop_column('skills')

    # ### end Alembic commands ###

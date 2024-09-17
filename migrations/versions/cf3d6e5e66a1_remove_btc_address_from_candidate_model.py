"""Remove btc_address from Candidate model

Revision ID: cf3d6e5e66a1
Revises: b05c22fe73c8
Create Date: 2024-09-17 17:29:39.512567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf3d6e5e66a1'
down_revision = 'b05c22fe73c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.drop_column('btc_address')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('candidate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('btc_address', sa.VARCHAR(length=100), nullable=True))

    # ### end Alembic commands ###

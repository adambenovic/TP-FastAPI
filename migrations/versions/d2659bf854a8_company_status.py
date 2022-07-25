"""company-status

Revision ID: d2659bf854a8
Revises: 4db135621f44
Create Date: 2022-05-02 14:04:05.848705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2659bf854a8'
down_revision = '4db135621f44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'status')
    # ### end Alembic commands ###

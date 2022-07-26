"""person-deleted-at

Revision ID: 1b4d3c53c780
Revises: ec8d111d46c4
Create Date: 2022-03-24 09:43:55.050358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b4d3c53c780'
down_revision = 'ec8d111d46c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'deleted_at')
    # ### end Alembic commands ###

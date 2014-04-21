"""change bandwith size

Revision ID: 42a3f495ec4
Revises: 12e8cae9c38
Create Date: 2014-04-21 19:23:04.632834

"""

# revision identifiers, used by Alembic.
revision = '42a3f495ec4'
down_revision = '12e8cae9c38'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('vpnsessions', 'bytes_up', existing_type=sa.Integer(), type_=sa.BigInteger())
    op.alter_column('vpnsessions', 'bytes_down', existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    op.alter_column('vpnsessions', 'bytes_up', existing_type=sa.BigInteger(), type_=sa.Integer())
    op.alter_column('vpnsessions', 'bytes_down', existing_type=sa.BigInteger(), type_=sa.Integer())


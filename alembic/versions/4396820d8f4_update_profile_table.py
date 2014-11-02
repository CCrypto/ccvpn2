"""update profile table

Revision ID: 4396820d8f4
Revises: 2e6851ff437
Create Date: 2014-11-02 02:18:49.875105

"""

# revision identifiers, used by Alembic.
revision = '4396820d8f4'
down_revision = '2e6851ff437'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('profiles', sa.Column('client_os', sa.String(), nullable=True, server_default=None))
    op.add_column('profiles', sa.Column('disable_ipv6', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('profiles', sa.Column('force_tcp', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('profiles', sa.Column('gateway_country', sa.String(), nullable=True, server_default=None))
    op.add_column('profiles', sa.Column('gateway_id', sa.Integer(), nullable=True, server_default=None))
    op.add_column('profiles', sa.Column('use_http_proxy', sa.String(), nullable=True, server_default=None))


def downgrade():
    op.drop_column('profiles', 'use_http_proxy')
    op.drop_column('profiles', 'gateway_id')
    op.drop_column('profiles', 'gateway_country')
    op.drop_column('profiles', 'force_tcp')
    op.drop_column('profiles', 'disable_ipv6')
    op.drop_column('profiles', 'client_os')

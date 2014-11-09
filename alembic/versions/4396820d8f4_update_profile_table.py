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
    client_os_enum = sa.Enum('windows', 'android', 'ubuntu', 'osx', 'freebox', 'other', name='client_os_enum')
    client_os_enum.create(op.get_bind(), checkfirst=False)
    protocols_enum = sa.Enum('udp', 'tcp', 'udpl', name='protocols_enum')
    protocols_enum.create(op.get_bind(), checkfirst=False)
    op.add_column('profiles', sa.Column('client_os', client_os_enum, nullable=True))
    op.add_column('profiles', sa.Column('protocol', protocols_enum, nullable=False, server_default='udp'))
    op.add_column('profiles', sa.Column('disable_ipv6', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('profiles', sa.Column('gateway_country', sa.String(), nullable=True, server_default=None))
    op.add_column('profiles', sa.Column('gateway_id', sa.Integer(), nullable=True, server_default=None))
    op.add_column('profiles', sa.Column('use_http_proxy', sa.String(), nullable=True, server_default=None))


def downgrade():
    op.drop_column('profiles', 'use_http_proxy')
    op.drop_column('profiles', 'gateway_id')
    op.drop_column('profiles', 'gateway_country')
    op.drop_column('profiles', 'protocol')
    op.drop_column('profiles', 'disable_ipv6')
    op.drop_column('profiles', 'client_os')
    sa.Enum(name='client_os_enum').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='protocols_enum').drop(op.get_bind(), checkfirst=False)


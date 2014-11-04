"""add default profile for existing users

Revision ID: 31cde2cf5e6
Revises: 4396820d8f4
Create Date: 2014-11-04 21:03:53.093993

"""

# revision identifiers, used by Alembic.
revision = '31cde2cf5e6'
down_revision = '4396820d8f4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    # Get a list of users without default profiles 
    fq = conn.execute('''
        select id
        from users
        where (select count(*)
               from profiles
               where profiles.uid=users.id and name='') = 0
    ''')
    users_without_dp = fq.fetchall()

    # Add one to them
    for user in users_without_dp:
        uid = user[0]
        
        iq = conn.execute('''
            insert into profiles(uid, name)
            values(%d, '')
        ''' % uid)

def downgrade():
    pass

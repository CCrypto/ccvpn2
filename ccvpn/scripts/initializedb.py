import os
import sys

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
import transaction

from ccvpn.models import DBSession, Base, User


def usage(argv, out=sys.stdout):
    cmd = os.path.basename(argv[0])
    out.write('usage: %s <config_uri>\n'
              '(example: "%s development.ini")\n' % (cmd, cmd))
    sys.exit(1)


def initialize_db():
    Base.metadata.create_all(DBSession.bind.engine)
    if not DBSession.query(User).filter_by(username='admin').count():
        with transaction.manager:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            DBSession.add(admin)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    initialize_db()


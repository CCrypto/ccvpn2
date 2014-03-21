import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from pyramid_mailer import mailer_factory_from_settings
from pyramid_mailer.message import Message
from ccvpn.models import DBSession, User

import logging
log = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('-S', '--send', action='store_true', default=False)
    parser.add_argument('--active', action='store_true', default=True)
    parser.add_argument('-s', '--subject', action='store')
    parser.add_argument('config')
    parser.add_argument('textfile')

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose is not None:
        verbose = int(args.verbose)
        if verbose == 1:
            log_level = logging.INFO
        elif verbose >= 2:
            log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    config_uri = args.config
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    mailer = mailer_factory_from_settings(settings)

    if not args.subject:
        print('Require a subject.')
        exit(1)

    message_in = open(args.textfile, 'r').read()
    if not message_in:
        print('Require a message.')
        exit(1)

    q = DBSession.query(User)
    if args.active:
        q = q.filter_by(is_paid=True)
    users = list(q.all())

    print('Sending to: %d users.' % (len(users)))
    if args.verbose:
        for u in users:
            print('- %s [%s]' % (u.email, u.username))

    for u in users:
        if not args.send:
            print('Not sending message to %s.' % u.email)
            continue
        message = Message(subject=args.subject,
                          recipients=[u.email],
                          body=message_in)
        mailer.send_immediately(message)
        

    


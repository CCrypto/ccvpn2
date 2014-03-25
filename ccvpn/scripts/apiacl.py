import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from ccvpn.models import DBSession, Gateway
import logging
log = logging.getLogger(__name__)


def add(args):
    t = Gateway()
    t.label = args.label
    if args.token == '-':
        args.token = input('Token (empty=random): ')
    if args.token:
        t.token = args.token
    if args.remote_addr:
        t.remote_addr = args.remote_addr
    DBSession.add(t)
    DBSession.commit()
    print('Inserted. token=%s' % t.token)


def revoke(args):
    q = DBSession.query(Gateway)
    if args.token == '-':
        args.token = input('Search token (empty=*): ')
    if args.token:
        q = q.filter_by(token=args.token)
    if args.label:
        q = q.filter_by(label=args.label)
    count = q.count()
    if count == 0:
        print('No token found.')
        return
    if count > 1:
        if args.force:
            print('Warning: mutliple tokens match.')
        else:
            print('Error: mutliple tokens match. Use -f to force.')
            return
    sure_str = 'Sure revoking %d tokens? [y/n] ' % q.count()
    if not args.yes and input(sure_str).lower() != 'y':
        return
    for t in q.all():
        print('Revoking token #%d (%s)...' % (t.id, t.label))
        DBSession.delete(t)


def main(argv=sys.argv):
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--verbose', action='count',
                        help='Increase verbosity')
    parser.add_argument('config')

    subparsers = parser.add_subparsers(title='subcommands')
    parser_add = subparsers.add_parser('add', help='add API access token')
    parser_add.set_defaults(func=add)
    parser_add.add_argument('label')
    parser_add.add_argument('-t', '--token', default='')
    parser_add.add_argument('-r', '--remote-addr', default='')

    parser_rev = subparsers.add_parser('rev', help='revoke API access token')
    parser_rev.set_defaults(func=revoke)
    parser_rev.add_argument('-n', '--label', default='')
    parser_rev.add_argument('-t', '--token', default='')
    parser_rev.add_argument('-r', '--remote-addr', default='')
    parser_rev.add_argument('-y', '--yes', default=False, action='store_true',
                            help='Dont ask for confirmation')
    parser_rev.add_argument('-f', '--force', default=False,
                            action='store_true',
                            help='Revoke even if multiple found')

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

    args.func(args)


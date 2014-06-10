"""
This script sends an email to accounts that are going to expire or has expired.
"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime, timedelta

from sqlalchemy import engine_from_config
from sqlalchemy.sql import or_
from sqlalchemy.sql import func
from pyramid.config import Configurator
from pyramid.paster import get_appsettings, setup_logging
from pyramid_mailer import mailer_factory_from_settings
from pyramid_mailer.message import Message
from pyramid.renderers import render
import transaction

from ccvpn.models import DBSession, User

import logging
log = logging.getLogger(__name__)


def send_notice(user, mailer):
    body = render('mail/expiry.mako', {
        'user': user,
    })

    message = Message(subject='CCVPN: Account expiration',
                      recipients=[user.email],
                      body=body)
    mailer.send_immediately(message)

    user.last_expiry_notice = datetime.now()


def get_future_expire(days=3):
    """This function get user accounts that will expire in a few days.
    """

    limit_date = datetime.now() + timedelta(days=days)

    q = DBSession.query(User) \
                 .filter(User.email != '') \
                 .filter(User.email != None)

    # Expire now < expiration < N days
    q = q.filter(User.paid_until > datetime.now())
    q = q.filter(User.paid_until < limit_date)

    # Only send notice if the last one was before the first time we could have
    # sent a notice
    # [last notice] < [expiration - 3days] < [this notice] < [expiration]
    if DBSession.bind.dialect.name == 'sqlite':
        a1 = func.julianday(User.paid_until)
        a2 = func.julianday(User.last_expiry_notice)
        cond = a1 - a2 > days
    else:
        cond = User.paid_until - User.last_expiry_notice > timedelta(days=days)

    q = q.filter(or_(User.last_expiry_notice == None, cond))

    users = list(q.all())

    log.debug('found %d accounts that expire in less than %d days',
              len(users), days)
    return users


def get_expired():
    """This function get expired user accounts.
    """

    q = DBSession.query(User) \
                 .filter(User.email != '') \
                 .filter(User.email != None)

    # Is expired
    q = q.filter(User.paid_until < datetime.now())

    # Only send notice if the last notice was before expiration
    q = q.filter(or_(User.last_expiry_notice == None,
                     User.last_expiry_notice < User.paid_until))

    users = list(q.all())

    log.debug('found %d expired accounts.', len(users))

    return users


def main(argv=sys.argv):
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('-s', '--send', action='store_true', default=False)
    parser.add_argument('--active', action='store_true', default=True)
    parser.add_argument('config')

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

    if 'mako.directories' not in settings:
        settings['mako.directories'] = 'ccvpn:templates/'
    if 'mako.imports' not in settings:
        settings['mako.imports'] = 'from ccvpn.filters import check'
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.commit()
    config.begin()

    mailer = mailer_factory_from_settings(settings)

    users = get_future_expire(7) + get_expired()

    if args.send:
        for u in users:
            print('sending notice to %s (%s)' % (u.username, u.email))
            send_notice(u, mailer)
        transaction.commit()
    else:
        for u in users:
            print('not sending notice to %s (%s)' % (u.username, u.email))
        print('Use -s to send messages')




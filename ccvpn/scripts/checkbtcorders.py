import os
import sys

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from ccvpn.models import DBSession, Order
from ccvpn.methods import BitcoinMethod

import logging
log = logging.getLogger(__name__)


def usage(argv, out=sys.stdout):
    cmd = os.path.basename(argv[0])
    out.write('usage: %s <config_uri>\n'
              '(example: "%s development.ini")\n' % (cmd, cmd))
    sys.exit(1)


def checkbtcorders(settings):
    method = BitcoinMethod()

    orders = DBSession.query(Order) \
        .filter_by(paid=False, method=Order.METHOD.BITCOIN)
    for order in orders:
        method.check_paid(settings, order)
        log.debug('Order#%d: amount=%f, paid=%f', order.id, order.amount,
                  order.paid_amount)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    checkbtcorders(settings)


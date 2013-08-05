from pyramid.response import Response
from pyramid.view import view_config
from .models import DBSession, User, Order, PaypalAPI
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from pyramid.httpexceptions import HTTPSeeOther, HTTPMovedPermanently, HTTPBadRequest, HTTPNotFound
import markdown
import os
import re
import transaction
import bitcoinrpc
import logging
from datetime import datetime, timedelta
from pyramid.renderers import render_to_response
log = logging.getLogger(__name__)

class PaypalMethod(object):
    def getAPI(self, request):
        if not PaypalMethod.api:
            api = PaypalAPI()
            api.test = bool(request.registry.settings.get('paypal.test', False))
            api.header_image = str(request.registry.settings.get('paypal.header_image', False))
            api.title = str(request.registry.settings.get('paypal.title', 'CCrypto VPN'))
            api.currency = str(request.registry.settings.get('paypal.currency', 'EUR'))
            api.address = str(request.registry.settings.get('paypal.address', 'paypal@ccrypto.org'))
            api.receiver = str(request.registry.settings.get('paypal.receiver', 'paypal@ccrypto.org'))
            PaypalMethod.api = api
        return PaypalMethod.api
        
    def init(self, request, order):
        month_price = float(request.registry.settings.get('paypal.month_price', 2))
        order.method = Order.METHOD.PAYPAL
        log.debug(round(month_price * (order.time.days / 30), 2))
        order.ammount = round(month_price * (order.time.days / 30), 2)

    def start(self, request, order):
        api = self.getAPI(request)
        link = api.make_link(order, request)
        return HTTPSeeOther(location=link)
    
    def callback(self, request, order):
        api = self.getAPI(request)
        if api.handle_notify(order, request):
            return HTTPOk()
        else:
            return HTTPBadRequest()

PaypalMethod.api = None

class BitcoinMethod(object):
    pass
'''
class BitcoinMethod(object):
    # TODO
bbitcoin_rpc = bitcoinrpc.connect_to_remote(
    settings.BITCOIND_USER, settings.BITCOIND_PASSWORD,
    settings.BITCOIND_HOST, settings.BITCOIND_PORT)
    pass
'''

METHOD_IDS = {
    Order.METHOD.PAYPAL: PaypalMethod,
    Order.METHOD.BITCOIN: BitcoinMethod,
}
METHODS = {
    'paypal': PaypalMethod,
    'bitcoin': BitcoinMethod,
}


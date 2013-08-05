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
from datetime import datetime, timedelta
from pyramid.renderers import render_to_response

class PaypalMethod(object):
    def init(self, request, order):
        if not PaypalMethod.api:
            api = PaypalAPI()
            api.test = bool(request.registry.settings.get('paypal.test', False))
            api.header_image = str(request.registry.settings.get('paypal.header_image', False))
            api.title = str(request.registry.settings.get('paypal.title', 'CCrypto VPN'))
            api.currency = str(request.registry.settings.get('paypal.currency', 'EUR'))
            api.address = str(request.registry.settings.get('paypal.address', 'paypal@ccrypto.org'))
            api.receiver = str(request.registry.settings.get('paypal.receiver', 'paypal@ccrypto.org'))
        month_price = float(request.registry.settings.get('paypal.month_price', 2))
        order.method = Order.METHOD.PAYPAL
        order.ammount = round(month_price * (order.time.days / 30), 2)

    def start(self, request, order):
        link = PaypalMethod.api.make_link(order, request)
        return HTTPSeeOther(location=link)
    
    def callback(self, request, order):
        if PaypalMethod.api.handle_notify(order, request):
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

class GiftcodeMethod(object):
    def init(self, request, order):
        order.method = Order.METHOD.GIFTCODE
        order.ammount = 0
        order.time = None
    
    def start(self, request, order):
        return render_to_response('ccvpn2_web:templates/order_giftcode.mako',
            {'order': order})
    
    def callback(self, request, order):
        if 'code' not in request.POST:
            return HTTPBadRequest()

METHODS = {
    'paypal': PaypalMethod,
    'bitcoin': BitcoinMethod,
}


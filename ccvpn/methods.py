from .models import DBSession, Order, PaypalAPI
from pyramid.httpexceptions import HTTPOk, HTTPSeeOther, HTTPBadRequest
import bitcoinrpc
import logging
import transaction
log = logging.getLogger(__name__)


class PaypalMethod(object):
    def getAPI(self, request):
        if not PaypalMethod.api:
            settings = request.registry
            api = PaypalAPI()
            api.test = bool(settings.get('paypal.test', False))
            api.header_image = str(settings.get('paypal.header_image', False))
            api.title = str(settings.get('paypal.title', 'CCrypto VPN'))
            api.currency = str(settings.get('paypal.currency', 'EUR'))
            api.address = str(settings.get('paypal.address',
                                           'paypal@ccrypto.org'))
            api.receiver = str(settings.get('paypal.receiver',
                                            'paypal@ccrypto.org'))
            PaypalMethod.api = api
        return PaypalMethod.api

    def init(self, request, order):
        settings = request.registry
        month_price = float(settings.get('paypal.month_price', 2))
        order.method = Order.METHOD.PAYPAL
        log.debug(round(month_price * (order.time.days / 30), 2))
        order.amount = round(month_price * (order.time.days / 30), 2)

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
    def getBTCRPC(self, settings):
        if not BitcoinMethod.rpc:
            user = settings.get('bitcoin.user', '')
            password = settings.get('bitcoin.password', '')
            host = settings.get('bitcoin.host', 'localhost')
            port = settings.get('bitcoin.port', 8332)
            if user == '':
                rpc = bitcoinrpc.connect_to_local()
            else:
                rpc = bitcoinrpc.connect_to_remote(user, password, host, port)
            BitcoinMethod.rpc = rpc
        return BitcoinMethod.rpc

    def init(self, request, order):
        settings = request.registry
        rpc = self.getBTCRPC(settings)
        account = str(settings.get('bitcoin.account', 'ccvpn2'))
        month_price = float(settings.get('bitcoin.month_price', 0.02))
        order.method = Order.METHOD.BITCOIN
        order.amount = round(month_price * (order.time.days / 30), 4)
        order.payment['btc_address'] = rpc.getnewaddress(account)

    def start(self, request, order):
        loc = request.route_url('order_view', hexid=hex(order.id)[2:])
        return HTTPSeeOther(location=loc)

    def check_paid(self, settings, order):
        rpc = self.getBTCRPC(settings)
        if 'btc_address' not in order.payment:
            return False
        addr = order.payment['btc_address']
        order.paid_amount = float(rpc.getreceivedbyaddress(addr))
        if order.paid_amount >= order.amount:
            order.paid = True
            order.user.add_paid_time(order.time)
        transaction.commit()

BitcoinMethod.rpc = None

METHOD_IDS = {
    Order.METHOD.PAYPAL: PaypalMethod,
    Order.METHOD.BITCOIN: BitcoinMethod,
}

METHODS = {
    'paypal': PaypalMethod,
    'bitcoin': BitcoinMethod,
}


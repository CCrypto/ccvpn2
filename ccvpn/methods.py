from .models import Order, PaypalAPI
from pyramid.httpexceptions import HTTPOk, HTTPSeeOther, HTTPBadRequest, HTTPServerError
import bitcoinrpc
import logging
import stripe
import stripe.error
log = logging.getLogger(__name__)


class Method(object):
    """
    Payement Method interface.

    __init__() is called on app start.

    Order creation:
    - init() is called to create an Order object
    - Order objects is saved to database
    - start() is called to get the next step
    """

    def __init__(self, settings):
        pass

    def init(self, user, time):
        raise NotImplementedError()

    def start(self, request, order):
        raise NotImplementedError()

    def view(self, request, order):
        raise NotImplementedError()

    def callback(self, request, order):
        raise NotImplementedError()


class PaypalMethod(Method):
    name = 'paypal'
    id = Order.METHOD.PAYPAL

    def __init__(self, settings):
        default_addr = 'paypal@ccrypto.org'
        self.api = PaypalAPI()
        self.api.test = bool(settings.get('paypal.test', False))
        self.api.header_image = settings.get('paypal.header_image', False)
        self.api.title = settings.get('paypal.title', 'CCrypto VPN')
        self.api.currency = settings.get('paypal.currency', 'EUR')
        self.api.address = settings.get('paypal.address', default_addr)
        self.api.receiver = settings.get('paypal.receiver', default_addr)
        self.month_price = float(settings.get('paypal.month_price', 2))

    def init(self, user, time):
        amount = round(self.month_price * (time.days / 30), 2)
        o = Order(user=user, time=time, amount=amount, method=self.id)
        return o

    def start(self, request, order):
        link = self.api.make_link(order, request)
        return HTTPSeeOther(location=link)

    def callback(self, request, order):
        if self.api.handle_notify(order, request):
            return HTTPOk()
        else:
            return HTTPBadRequest()


class StripeMethod(Method):
    name = 'stripe'
    id = Order.METHOD.STRIPE

    def __init__(self, settings):
        stripe.api_key = settings.get('stripe.api_key')
        self.pkey = settings.get('stripe.pkey')
        self.month_price = float(settings.get('stripe.month_price', 2.00))

    def init(self, user, time):
        amount = self.month_price * (time.days / 30)
        o = Order(user=user, time=time, amount=amount, method=self.id)
        return o

    def start(self, request, order):
        loc = request.route_url('order_view', hexid=hex(order.id)[2:])
        return HTTPSeeOther(location=loc)

    def view(self, request, order):
        months = int(order.time.days / 30)
        username = order.user.username
        return {
            'pkey': self.pkey,
            'amount': int(order.amount * 100),
            'name': 'CCrypto VPN',
            'description': '%d months for %s' % (months, username),
            'currency': 'eur',
        }

    def callback(self, request, order):
        token = request.POST.get('stripeToken')
        if not token:
            return HTTPBadRequest('missing stripeToken')
        months = int(order.time.days / 30)
        username = order.user.username
        try:
            charge = stripe.Charge.create(
                amount=int(order.amount * 100),
                currency='eur',
                card=token,
                description='%d months for %s' % (months, username),
            )
            order.payment['charge_id'] = charge['id']
            if charge['refunded'] or not charge['paid']:
                request.message.error('Error: The order has not been payed or '
                                      'has been refunded')
                loc = request.route_url('order_view', hexid=hex(order.id)[2:])
                return HTTPSeeOther(location=loc)
            order.paid_amount = float(charge['amount']) / 100.0
            order.paid = True
            order.user.add_paid_time(order.time)
            loc = request.route_url('order_view', hexid=hex(order.id)[2:])
            return HTTPSeeOther(location=loc)
        except stripe.error.CardError as e:
            message = e.json_body['error']['message']
            request.message.error('Card error: ' + message)
            order.payment['error'] = message
            loc = request.route_url('order_view', hexid=hex(order.id)[2:])
            return HTTPSeeOther(location=loc)
        except stripe.error.AuthenticationError:
            log.critical('Authentication with Stripe failed')
            return HTTPServerError()
        except stripe.error.StripeError as e:
            log.critical('Stripe error: '+str(e))
            return HTTPServerError()


class BitcoinMethod(Method):
    name = 'bitcoin'
    id = Order.METHOD.BITCOIN

    def __init__(self, settings):
        user = settings.get('bitcoin.user', '')
        password = settings.get('bitcoin.password', '')
        host = settings.get('bitcoin.host', 'localhost')
        port = settings.get('bitcoin.port', 8332)
        if user == '':
            self.rpc = bitcoinrpc.connect_to_local()
        else:
            self.rpc = bitcoinrpc.connect_to_remote(user, password, host, port)
        self.month_price = float(settings.get('bitcoin.month_price', 0.02))
        self.account = settings.get('bitcoin.account', 'ccvpn2')

    def init(self, user, time):
        amount = round(self.month_price * (time.days / 30), 4)
        o = Order(user=user, time=time, amount=amount, method=self.id)
        o.payment['btc_address'] = self.rpc.getnewaddress(self.account)
        return o

    def start(self, request, order):
        loc = request.route_url('order_view', hexid=hex(order.id)[2:])
        return HTTPSeeOther(location=loc)

    def check_paid(self, order):
        if 'btc_address' not in order.payment:
            return False
        addr = order.payment['btc_address']
        order.paid_amount = float(self.rpc.getreceivedbyaddress(addr))
        if order.paid_amount >= order.amount:
            order.paid = True
            order.user.add_paid_time(order.time)


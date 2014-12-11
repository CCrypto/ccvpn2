from urllib.parse import urlencode
from urllib.request import urlopen


class PaypalAPI(object):
    api_base = ''
    test = False
    header_image = False
    title = 'CCrypto VPN'
    currency = 'EUR'
    address = 'paypal@ccrypto.org'
    receiver = 'paypal@ccrypto.org'

    def __init__(self, test=False):
        self.test = test
        if test:
            self.api_base = 'https://www.sandbox.paypal.com/'
        else:
            self.api_base = 'https://www.paypal.com/'

    def make_link(self, order, request):
        baseurl = self.api_base + '/cgi-bin/webscr?'
        hexid = hex(order.id)[2:]
        params = {
            'cmd': '_xclick',
            'notify_url': request.route_url('order_callback', hexid=hexid),
            'item_name': self.title,
            'amount': order.amount,
            'currency_code': self.currency,
            'business': self.address,
            'no_shipping': '1',
            'return': request.route_url('order_view', hexid=hexid),
            'cancel_return': request.route_url('order_view', hexid=hexid),
        }
        if self.header_image:
            params['cpp_header_image'] = self.header_image
        url = baseurl + urlencode(params)
        return url

    def handle_notify(self, order, request):
        # validate notify
        v_url = self.api_base + '/cgi-bin/webscr?cmd=_notify-validate'
        v_req = urlopen(v_url, data=bytes(request.body))
        v_res = v_req.read()
        if v_res != b'VERIFIED':
            return False

        try:
            params = request.POST

            if 'test_ipn' in params:
                assert self.test and params['test_ipn'] == '1', \
                    'Test API notify'

            if params['payment_status'] == 'Refunded':
                # Refund
                if type(order.payment) is not dict or len(order.payment) == 0:
                    order.payment = {
                        'payerid': params['payer_id'],
                        'payeremail': params['payer_email'],
                    }
                order.payment['status'] = 'refunded'
                order.paid = False
                # FIXME: maybe remove some time
                return True
            elif params['payment_status'] == 'Completed':
                assert self.receiver == params['receiver_email'], \
                    'Wrong receiver: ' + params['receiver_email']
                assert self.currency == params['mc_currency'], \
                    'Wrong currency: ' + params['mc_currency']
                assert params['txn_type'] == 'web_accept', \
                    'Wrong transaction type: ' + params['txn_type']

                order.paid_amount = float(params['mc_gross'])
                assert order.paid_amount >= order.amount, \
                    'HAX! Paid %f, ordered %f.' % (
                        order.paid_amount, order.amount)

                # Store some data about the order
                order.payment = {
                    'txnid': params['txn_id'],
                    'payerid': params['payer_id'],
                    'payeremail': params['payer_email'],
                }
                order.paid = True
                order.user.add_paid_time(order.time)
                return True
            else:
                # Not implemented, ignore it
                print('received: ', params)
                return True

        except KeyError as ke:
            # Invalid notification - do not reply to it.
            print('invalid notification: ' + str(ke))
            return False
        except AssertionError as error:
            # Well-formed notification with bad input.
            # We dont want to receive it again
            order.payment = dict(error=str(error))
            print('Error: ' + str(error))
            return True

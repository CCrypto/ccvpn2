from sqlalchemy import Column, Integer, Text, String, Boolean, BigInteger, DateTime, ForeignKey, UnicodeText, Float, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta
import json
import random
import logging
from urllib.parse import urlencode
from urllib.request import urlopen

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def random_access_token():
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[random.randint(0,base-1)] for n in xrange(32)])

def random_gift_code():
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[random.randint(0,base-1)] for n in xrange(16)])
    
class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

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
        baseurl = self.api_base+'/cgi-bin/webscr?'
        params = {
            'cmd' : '_donations',
            'notify_url' : request.route_url('paypal_ipn', order=order.id),
            'item_name' : self.title,
            'currency_code' : self.currency,
            'business' : self.address,
            'no_shipping' : '1',
            'return' : request.route_url('orders'),
            'cancel_return' : request.route_url('home'),
        }
        if self.header_image:
            params['cpp_header_image'] = self.header_image
        url = baseurl + urlencode(params)
        return url
    
    def handle_notify(self, order, request):
        # validate notify
        v_url = self.api_base+'/cgi-bin/webscr?cmd=_notify-validate'
        mybody = request.body.decode("utf-8")
        v_req = urlopen(v_url, data=bytes(request.body))
        v_res = v_req.read()
        if v_res != b'VERIFIED':
            return False
        
        try:
            params = request.POST
            
            if 'test_ipn' in params:
                assert self.test and params['test_ipn']=='1', \
                    'Test API notify'
            
            if params['payment_status'] == 'Refunded':
                # Refund
                if type(order.payment) is not dict or len(order.payment) == 0:
                    order.payment = {
                        'payerid' : params['payer_id'],
                        'payeremail' : params['payer_email'],
                    }
                order.payment['status'] = 'refunded'
                order.ok = False
                return True
            elif params['payment_status'] == 'Completed':
                assert self.receiver == params['receiver_email'], \
                    'Wrong receiver: '+params['receiver_email']
                assert self.currency ==  params['mc_currency'], \
                    'Wrong currency: '+params['mc_currency']
                assert params['txn_type'] == 'web_accept', \
                    'Wrong transaction type: '+params['txn_type']
                
                order.paid_ammount = float(params['mc_gross'])
                assert order.paid_ammount >= order.ammount, \
                    'HAX! Paid %f, ordered %f.' % (
                        order.paid_ammount, order.ammount)
                
                # Store some data about the order
                order.payment = {
                    'txnid' : params['txn_id'],
                    'payerid' : params['payer_id'],
                    'payeremail' : params['payer_email'],
                }
                order.ok = True
                return True
            else:
                # Not implemented, ignore it
                print('received : ', params)
                return True

        except KeyError as ke:
            # Invalid notification - do not reply to it.
            print('invalid notification : '+str(ke))
            return False
        except AssertionError as error:
            # Well-formed notification with bad input.
            # We dont want to receive it again
            order.payment = dict(error=str(error))
            print('Error: '+str(error))
            return True


class User(Base):
    __tablename__ = 'users'
    id          = Column(Integer, primary_key=True, nullable=False)
    username    = Column(String(length=32), unique=True, nullable=False)
    password    = Column(postgresql.BYTEA(length=96), nullable=False)
    email       = Column(String(length=256), nullable=True, default=None)
    is_active   = Column(Boolean, nullable=False, default=True)
    is_admin    = Column(Boolean, nullable=False, default=False)
    month_bw    = Column(BigInteger, nullable=False, default=0)
    signup_date = Column(DateTime, nullable=False, default=datetime.now)
    last_login  = Column(DateTime, nullable=True, default=None)
    paid_until  = Column(DateTime, nullable=True, default=None)
    
    def is_paid(self):
        return self.paid_until != None and self.paid_until > datetime.now()
    
    def add_paid_time(self, time):
        if not self.is_paid():
            self.paid_until = datetime.now()
        self.paid_until += time

    def __str__(self):
        return '<User %s #%d>'%(self.username, self.id)

def get_user(request):
    if 'user_id' not in request.session:
        return None

    uid = request.session['user_id']
    user = DBSession.query(User).filter_by(id=uid) .first()
    if not user:
        del request.session['user_id']
        return None
    return user

class RemoteAddrModel(Base):
    __tablename__ = 'gatewayaddrs'
    id         = Column(Integer, primary_key=True, nullable=False)
    ipversion  = Column(Integer, nullable=False)
    location   = Column(String(length=32), nullable=False)

class GiftCodes(Base):
    __tablename__ = 'giftcodes'
    id      = Column(Integer, primary_key=True, nullable=False)
    code    = Column(String(16), primary_key=True, nullable=False, default=random_gift_code)
    enabled = Column(Boolean, default=True, nullable=False)
    onetime = Column(Boolean, default=True, nullable=False)
    used    = Column(Integer, default=0, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    class METHOD:
        BITCOIN = 0
        PAYPAL  = 1
        GIFTCODE= 2

    id          = Column(Integer, primary_key=True, nullable=False)
    uid         = Column(ForeignKey('users.id'))
    start_date  = Column(DateTime, nullable=False, default=datetime.now)
    close_date  = Column(DateTime, nullable=True)
    ammount     = Column(Float, nullable=False)
    paid_ammount= Column(Float, nullable=False)
    method      = Column(Integer, nullable=False)
    paid        = Column(Boolean, nullable=False, default=False)
    paymentdata = Column(JSONEncodedDict(), nullable=True)

class APIAccessToken(Base):
    __tablename__ = 'apiaccesstok'
    id          = Column(Integer, primary_key=True, nullable=False)
    token       = Column(String(32), primary_key=True, nullable=False, default=random_access_token)
    label       = Column(String(256), nullable=True)
    remote_addr = Column(postgresql.INET, nullable=True)
    expire_date = Column(DateTime, nullable=True)




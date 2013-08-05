from sqlalchemy import Column, Integer, Text, String, Boolean, BigInteger, DateTime, ForeignKey, UnicodeText, Float, TypeDecorator, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta
import json
import random
import logging
import re
import hashlib
from urllib.parse import urlencode
from urllib.request import urlopen

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

def random_access_token():
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[random.randint(0,base-1)] for n in range(32)])

def random_gift_code():
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[random.randint(0,base-1)] for n in range(16)])

def random_bytes(length):
    return bytearray([random.randint(0,0xff) for n in range(length)])

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
        hexid = hex(order.id)[2:]
        params = {
            'cmd' : '_xclick',
            'notify_url' : request.route_url('order_callback', hexid=hexid),
            'item_name' : self.title,
            'amount' : order.ammount,
            'currency_code' : self.currency,
            'business' : self.address,
            'no_shipping' : '1',
            'return' : request.route_url('order_view', hexid=hexid),
            'cancel_return' : request.route_url('order_view', hexid=hexid),
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

    giftcodes_used = relationship('GiftCode', backref='user')
    orders = relationship('Order', backref='user')

    username_re = re.compile('^[a-zA-Z0-9_-]{2,32}$')
    email_re    = re.compile('^.+@.+$')

    def is_paid(self):
        return self.paid_until != None and self.paid_until > datetime.now()
    
    def add_paid_time(self, time):
        if not self.is_paid():
            self.paid_until = datetime.now()
        self.paid_until += time

    def paid_days_left(self):
        if self.is_paid():
            days = (self.paid_until - datetime.now()).days
            return days if days > 0 else 1
        else:
            return 0

    def validate_username(self, username):
        return self.username_re.match(username)

    def validate_email(self, email):
        return self.email_re.match(email)

    def validate_password(self,clearpw):
        return 0 < len(clearpw) < 256

    def set_password(self, clearpw):
        if 0 < len(clearpw) < 256:
            salt = random_bytes(32)
            password = bytearray(clearpw, 'utf-8')
            hash = hashlib.sha512(salt+password).digest()
            self.password = salt + hash
            return True
        return False

    def check_password(self, clearpw):
        if len(self.password) != 96:
            return False
        salt = self.password[:32]
        password = bytearray(clearpw, 'utf-8')
        hash = hashlib.sha512(salt+password).digest()
        return self.password[32:96] == hash

class GiftCode(Base):
    __tablename__ = 'giftcodes'
    id      = Column(Integer, primary_key=True, nullable=False)
    code    = Column(String(16), primary_key=True, nullable=False, default=random_gift_code)
    time    = Column(Interval, default=timedelta(days=30), nullable=False)
    used    = Column(ForeignKey('users.id'), nullable=True)

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
    paid_ammount= Column(Float, nullable=False, default=0)
    time        = Column(Interval, nullable=True)
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



def get_user(request):
    if 'uid' not in request.session:
        return None

    uid = request.session['uid']
    user = DBSession.query(User).filter_by(id=uid) .first()
    if not user:
        del request.session['uid']
        return None
    return user

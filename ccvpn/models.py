from sqlalchemy import (
    TypeDecorator, Column, ForeignKey,
    Integer, Float, DateTime, Boolean, BigInteger,
    String, UnicodeText, Text, LargeBinary, Interval,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects import postgresql  # INET
from sqlalchemy.sql.expression import true, false
from zope.sqlalchemy import ZopeTransactionExtension
from datetime import datetime, timedelta
import json
import random
import logging
import re
import hashlib
import requests
import socket
from beaker import cache
from urllib.parse import urlencode
from urllib.request import urlopen

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(keep_session=False)))
prng = random.SystemRandom()


class Base(object):
    @classmethod
    def one(cls, **kwargs):
        return DBSession.query(cls).filter_by(**kwargs).one()

    @classmethod
    def all(cls, **kwargs):
        return DBSession.query(cls).filter_by(**kwargs).all()


Base = declarative_base(cls=Base)


def random_access_token():
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[prng.randint(0, base - 1)] for n in range(32)])


def random_gift_code():
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(charset)
    return ''.join([charset[prng.randint(0, base - 1)] for n in range(16)])


def random_bytes(length):
    return bytearray([prng.randint(0, 0xff) for n in range(length)])


class JSONEncodedDict(TypeDecorator):
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value:
            return json.dumps(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        else:
            return dict()


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class INETWrapper(TypeDecorator):
    impl = String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.INET())
        else:
            return dialect.type_descriptor(String())


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


class IcingaError(Exception):
    pass


class IcingaQuery(object):
    def __init__(self, urlbase, auth):
        self.baseurl = urlbase
        self.auth = auth

        try:
            content = self._get_availcgi()
            data = json.loads(content)
            self.report = data['avail']['service_availability']['services']
        except (requests.RequestException, socket.timeout) as e:
            raise IcingaError('failed to connect: ' + str(e))
        except (ValueError, KeyError) as e:
            raise IcingaError('failed to decode icinga response (%s)' % str(e))

    @cache.cache_region('short_term')
    def _get_availcgi(self):
        hostservices = 'all^all'
        timeperiod = 'last31days'
        backtrack = 4
        url = '/avail.cgi?hostservice=%s&timeperiod=%s&backtrack=%d&jsonoutput'
        url = url % (hostservices, timeperiod, backtrack)
        r = requests.get(self.baseurl + url,
                         auth=self.auth, verify=False, timeout=2)
        content = r.content.decode('utf-8')

        # When querying services availability, icinga can break the JSON
        content = re.sub(',\n*(\]|\})', '\\1', content)

        return content

    def get_uptime(self, host, service):
        try:
            def fn(h):
                return h['host_name'] == host and \
                       h['service_description'] == service
            svcdata = next(filter(fn, self.report))
            uptime = int(svcdata['percent_known_time_ok'])
        except (KeyError, ValueError) as e:
            raise IcingaError('failed to parse icinga report (%s)' % str(e),
                              host, service)
        except StopIteration:
            raise IcingaError('host/service unknown to icinga', host, service)
        return uptime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, doc='ID')
    username = Column(String(length=32), unique=True, nullable=False,
                      doc='Username')
    password = Column(LargeBinary(length=96), nullable=False, doc='Password')
    email = Column(String(length=256), nullable=True, default=None,
                   doc='E-mail')
    is_active = Column(Boolean, nullable=False, default=True, doc='Active?')
    is_admin = Column(Boolean, nullable=False, default=False, doc='Admin?')
    month_bw = Column(BigInteger, nullable=False, default=0)
    signup_date = Column(DateTime, nullable=False, default=datetime.now)
    last_login = Column(DateTime, nullable=True, default=None)
    paid_until = Column(DateTime, nullable=True, default=None)
    referrer_id = Column(ForeignKey('users.id'), nullable=True)

    giftcodes_used = relationship('GiftCode', backref='user')
    orders = relationship('Order', backref='user')
    paid_orders = relationship('Order', viewonly=True,
                               primaryjoin='and_(Order.uid == User.id, Order.paid == True)')
    profiles = relationship('Profile', backref='user')
    pw_reset_tokens = relationship('PasswordResetToken', backref='user')
    sessions = relationship('VPNSession', backref='user')

    username_re = re.compile('^[a-zA-Z0-9_-]{2,32}$')
    email_re = re.compile('^.+@.+$')

    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password', None)
        if password:
            self.set_password(password)
        super().__init__(*args, **kwargs)

    @hybrid_property
    def is_paid(self):
        return self.paid_until is not None and self.paid_until > datetime.now()

    def add_paid_time(self, time):
        new_date = self.paid_until
        if not self.is_paid:
            new_date = datetime.now()
        try:
            new_date += time
        except OverflowError:
            return
        self.paid_until = new_date

    def paid_time_left(self):
        if self.is_paid:
            return self.paid_until - datetime.now()
        else:
            return timedelta()

    def paid_days_left(self):
        if self.is_paid:
            days = (self.paid_until - datetime.now()).days
            return days if days > 0 else 1
        else:
            return 0

    @classmethod
    def validate_username(cls, username):
        return username and cls.username_re.match(username)

    @classmethod
    def validate_email(cls, email):
        return email and cls.email_re.match(email) and len(email) <= 256

    @classmethod
    def validate_password(self, clearpw):
        return clearpw and 0 < len(clearpw) < 256

    def set_password(self, clearpw):
        salt = random_bytes(32)
        password = bytearray(clearpw, 'utf-8')
        hash = hashlib.sha512(salt + password).digest()
        self.password = salt + hash
        return True

    def check_password(self, clearpw):
        if not self.password or len(self.password) != 96:
            return False
        salt = self.password[:32]
        password = bytearray(clearpw, 'utf-8')
        hash = hashlib.sha512(salt + password).digest()
        return self.password[32:96] == hash

    def __str__(self):
        return self.username

    @classmethod
    def is_used(cls, username, email):
        nc = DBSession.query(func.count(User.id).label('nc')) \
            .filter_by(username=username) \
            .subquery()
        ec = DBSession.query(func.count(User.id).label('ec')) \
            .filter_by(email=email) \
            .subquery()
        c = DBSession.query(nc, ec).first()
        return (c.nc, c.ec)


class PasswordResetToken(Base):
    __tablename__ = 'pwresettoken'
    id = Column(Integer, primary_key=True)
    uid = Column(ForeignKey('users.id'), nullable=False)
    token = Column(String(32), nullable=False)
    expire_date = Column(DateTime, nullable=True)

    def __init__(self, uid, token=None, expire=None):
        if isinstance(uid, User):
            uid = uid.id

        default_ttl = timedelta(days=2)

        self.uid = uid
        self.token = token or random_access_token()
        self.expire_date = expire or datetime.now() + default_ttl


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, doc='ID')
    uid = Column(ForeignKey('users.id'))
    name = Column(String(16), nullable=False, doc='Name')
    password = Column(Text, nullable=True, doc='Key')

    sessions = relationship('VPNSession', backref='profile')

    def validate_name(self, name):
        return re.match('^[a-zA-Z0-9]{1,16}$', name)

    list_fields = ('id', 'uid', 'name')
    edit_fields = ('id', 'uid', 'name', 'password')


class AlreadyUsedGiftCode(Exception):
    pass


class GiftCode(Base):
    __tablename__ = 'giftcodes'
    id = Column(Integer, primary_key=True, nullable=False, doc='ID')
    code = Column(String(16), unique=True, nullable=False, doc='Code',
                  default=random_gift_code)
    time = Column(Interval, default=timedelta(days=30), nullable=False,
                  doc='Time')
    free_only = Column(Boolean, default=False, nullable=False,
                       server_default=false())
    used = Column(ForeignKey('users.id'), nullable=True)

    def __init__(self, time=None, code=None, used=None):
        if isinstance(used, User):
            used = used.id

        self.time = time or timedelta(days=30)
        self.used = used
        self.code = code or random_gift_code()

    @property
    def username_if_used(self):
        '''User'''
        if self.used and self.user:
            return self.user.username
        else:
            return False

    def use(self, user, reuse=False):
        """Use this GiftCode on user

        :param user: User
        :param reuse: bool allow to reuse a code?

        """

        if self.used and not reuse:
            raise AlreadyUsedGiftCode()
        if self.free_only and user.is_paid:
            raise AlreadyUsedGiftCode()
        self.used = user.id
        user.add_paid_time(self.time)

    def __str__(self):
        return self.code

    list_fields = ('id', 'code', 'time', 'username_if_used')
    edit_fields = ('id', 'code', 'time', 'free_only', 'used')


class OrderNotPaid(Exception):
    pass


class Order(Base):
    __tablename__ = 'orders'

    class METHOD:
        BITCOIN = 0
        PAYPAL = 1
        STRIPE = 2

    id = Column(Integer, primary_key=True)
    uid = Column(ForeignKey('users.id'))
    start_date = Column(DateTime, nullable=False, default=datetime.now)
    close_date = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False, default=0)
    time = Column(Interval, nullable=True)
    method = Column(Integer, nullable=False)
    paid = Column(Boolean, nullable=False, default=False)
    payment = Column(MutableDict.as_mutable(JSONEncodedDict), nullable=True)

    list_fields = ('id', 'user', 'start_date', 'amount', 'paid_amount', 'time',
                   'method', 'paid')
    edit_fields = ('id', 'user', 'start_date', 'close_date', 'amount',
                   'paid_amount', 'time', 'method', 'paid', 'payment')

    def is_paid(self):
        return self.paid_amount >= self.amount

    def close(self, force=False):
        """Close a paid order.

        :raises: OrderNotPaid
        """
        if not self.is_paid() and not force:
            raise OrderNotPaid(self)

        self.paid = True
        self.user.add_paid_time(self.time)

        if self.user.referrer_id:
            try:
                referrer = User.one(id=self.user.referrer_id)
                referrer.add_paid_time(timedelta(days=14))
            except NoResultFound:
                pass
            # Given 14d or inexistent, we can remove it.
            self.user.referrer_id = None

    def __init__(self, user, amount, time, method, paid_amount=0, ttl=None):
        self.uid = user.id if isinstance(user, User) else user
        self.amount = amount
        self.time = time
        self.paid_amount = paid_amount
        self.paid = paid_amount >= amount
        self.payment = {}
        self.method = method

        ttl = ttl or timedelta(days=30)

        self.start_date = datetime.now()
        self.close_date = datetime.now() + ttl

    def __str__(self):
        return hex(self.id)[2:]

    def __repr__(self):
        return '<Order %d by %s, %s>' % (self.id, self.user.username,
                                         self.time)


class Gateway(Base):
    __tablename__ = 'gateways'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    isp_name = Column(String(32), nullable=False)
    isp_url = Column(String, nullable=False)
    country = Column(String(2), nullable=False)
    token = Column(String(32), nullable=False, default=random_access_token)
    ipv4 = Column(String, nullable=True)
    ipv6 = Column(String, nullable=True)
    bps = Column(BigInteger, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True,
                     server_default=true())

    sessions = relationship('VPNSession', backref='gateway')

    list_fields = ('id', 'name', 'ipv4', 'ipv6', 'enabled')
    edit_fields = ('id', 'name', 'isp_name', 'isp_url', 'country', 'token',
                   'ipv4', 'ipv6', 'bps', 'enabled')

    def __repr__(self):
        return '<Gateway %s.%s>' % (self.name, self.country)


class VPNSession(Base):
    __tablename__ = 'vpnsessions'
    id = Column(Integer, primary_key=True)
    gateway_id = Column(ForeignKey('gateways.id'), nullable=False)
    gateway_version = Column(Integer, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    profile_id = Column(ForeignKey('profiles.id'), nullable=True)
    connect_date = Column(DateTime, default=datetime.now, nullable=False)
    disconnect_date = Column(DateTime, nullable=True)
    remote_addr = Column(String, nullable=False)
    bytes_up = Column(Integer, nullable=True)
    bytes_down = Column(Integer, nullable=True)

    def __repr__(self):
        return '<VPNSession %d gw %d %s user %d, %s -> %s>' % (
            self.id, self.gateway_id, self.gateway_version, self.user_id,
            self.connect_date, self.disconnect_date)


def get_user(request):
    if 'uid' not in request.session:
        return None

    uid = request.session['uid']
    user = DBSession.query(User).filter_by(id=uid).first()
    if not user:
        del request.session['uid']
        return None
    return user


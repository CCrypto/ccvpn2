import logging
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings
from ccvpn import views

from .models import DBSession, Base, get_user, User

logger = logging.getLogger(__name__)


class AuthenticationPolicy(object):
    def authenticated_userid(self, request):
        return request.user

    def unauthenticated_userid(self, request):
        return None

    def effective_principals(self, request):
        if not request.user:
            return []
        ep = []
        if request.user.is_active:
            ep.append('logged')
        if request.user.is_admin:
            ep.append('admin')
        if request.user.is_paid:
            ep.append('paid')
        return ep


class Messages(object):
    ''' Simple class that manages session flash messages '''
    def __init__(self, request):
        self.request = request
        self.session = request.session

    def add(self, level, text):
        self.session.flash((level, text))

    def error(self, text):
        return self.add('error', text)

    def info(self, text):
        return self.add('info', text)


class AuthorizationPolicy(object):
    ''' Why the fuck is ACLAuthorizationPolicy so complicated ? '''
    def permits(self, context, principals, permission):
        return permission in principals


def setup_routes(config):
    a = config.add_route

    # Public routes
    a('home', '/')
    a('page', '/page/{page:[a-zA-Z0-9_-]+}')
    a('status', '/status')
    a('ca_crt', '/ca.crt')

    # Account related
    a('account_redirect', '/account')
    a('account', '/account/')
    a('account_login', '/account/login')
    a('account_logout', '/account/logout')
    a('account_forgot', '/account/forgot')
    a('account_reset', '/account/reset/{token:[a-zA-Z0-9]+}')
    a('account_signup', '/account/signup')
    a('order_post', '/order/', request_method='POST')
    a('order_view', '/order/view/{hexid:[a-f0-9]+}')
    a('order_callback', '/order/callback/{hexid:[a-f0-9]+}')
    a('config', '/config/ccrypto.ovpn')

    # Admin related
    a('admin_home', '/admin/')
    a('admin_graph', '/admin/graph/{name}.svg')
    a('admin_users', '/admin/users')
    a('admin_orders', '/admin/orders')
    a('admin_giftcodes', '/admin/giftcodes')
    a('admin_apiaccesstokens', '/admin/apiaccesstokens')
    a('admin_gateways', '/admin/gateways')

    # Server API
    a('api_gateway_auth', '/api/gateway/auth')
    a('api_gateway_disconnect', '/api/gateway/disconnect')
    a('api_gateway_connect', '/api/gateway/connect')


def referral_handler(request):
    ref = request.GET.get('ref')
    if not ref:
        return None
    try:
        iref = int(ref)
    except ValueError:
        return None
    u = DBSession.query(User).filter_by(id=iref).first()
    if not u:
        return None
    # Overwrite get_referrer to return u for this request
    request.referrer = u
    return u


def get_referrer(request):
    if 'referral_id' not in request.cookies:
        return None
    try:
        iref = int(request.cookies['referral_id'])
    except ValueError:
        return None
    u = DBSession.query(User).filter_by(id=iref).first()
    if not u:
        return None
    return u


def referral_handler_factory(handler, registry):
    def decorator(request):
        u = referral_handler(request)
        response = handler(request)
        if u:
            response.set_cookie('referral_id', str(u.id), overwrite=True)
        return response
    return decorator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    if 'sqlalchemy.url' in settings:
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

    if not 'mako.directories' in settings:
        settings['mako.directories'] = 'ccvpn:templates/'
    if not 'mako.imports' in settings:
        settings['mako.imports'] = 'from ccvpn.filters import check'

    session_factory = session_factory_from_settings(settings)
    authentication = AuthenticationPolicy()
    authorization = AuthorizationPolicy()

    config = Configurator(settings=settings,
                          authentication_policy=authentication,
                          authorization_policy=authorization)

    includes = settings.get('pyramid.includes', {})
    config.include('pyramid_mako')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    if 'pyramid_mailer.testing' not in includes:
        config.include('pyramid_mailer')
    config.set_session_factory(session_factory)
    config.add_request_method(get_user, 'user', reify=True, property=True)
    config.add_request_method(get_referrer, 'referrer', reify=True,
                              property=True)
    config.add_request_method(Messages, 'messages', reify=True,
                              property=True)
    config.add_tween('ccvpn.referral_handler_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)
    setup_routes(config)
    config.scan()

    ca_path = settings.get('openvpn.ca-cert', None)
    if ca_path:
        views.account.openvpn_ca = open(ca_path, 'r').read()
    else:
        views.account.openvpn_ca = ''

    gw = settings.get('openvpn.gateway', 'gw.vpn.ccrypto.org')
    views.account.openvpn_gateway = gw

    return config.make_wsgi_app()


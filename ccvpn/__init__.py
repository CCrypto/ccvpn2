import logging
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings
from ccvpn import views
from ccvpn import methods

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
    #a('admin_home', '/admin/')
    a('admin_graph', '/admin/graph/{name}.svg')
    a('admin_traversal', '/admin/*traverse', factory=views.admin.root_factory)

    # Server API
    a('api_gateway_auth', '/api/gateway/auth')
    a('api_gateway_disconnect', '/api/gateway/disconnect')
    a('api_gateway_connect', '/api/gateway/connect')

    # Public API
    a('api_public_gateways', '/api/public/gateways')


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


def my_locale_negotiator(request):
    if 'l' in request.GET:
        locale = request.GET['l']
        logger.debug('Locale (GET): %s', locale)
        def save_locale(request, response):
            response.set_cookie('locale', request.locale_name)
        request.add_response_callback(save_locale)
        return locale

    if 'locale' in request.cookies:
        locale = request.cookies['locale']
        logger.debug('Locale (cookie): %s', locale)
        return locale



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

    config.add_translation_dirs('ccvpn:locale')
    config.add_subscriber('ccvpn.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('ccvpn.subscribers.add_localizer',
                          'pyramid.events.NewRequest')
    config.set_locale_negotiator(my_locale_negotiator)

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

    methods_objs = {}
    for c in methods.Method.__subclasses__():
        obj = c(settings)
        methods_objs[c.name] = obj
        methods_objs[c.id] = obj
    config.add_request_method(lambda r: methods_objs, 'payment_methods',
                              reify=True, property=True)
    methods.payement_methods = methods_objs

    ca_path = settings.get('openvpn.ca-cert', None)
    if ca_path:
        views.account.openvpn_ca = open(ca_path, 'r').read()
    else:
        views.account.openvpn_ca = ''
        logger.warning('Failed to open OpenVPN CA file: %s' % ca_path)

    gw = settings.get('openvpn.gateway', 'gw.204vpn.net')
    views.account.openvpn_gateway = gw

    return config.make_wsgi_app()


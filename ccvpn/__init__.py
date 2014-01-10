from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings
from ccvpn import views

from .models import DBSession, Base, get_user


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


class AuthorizationPolicy(object):
    ''' Why the fuck is ACLAuthorizationPolicy so complicated ? '''
    def permits(self, context, principals, permission):
        return permission in principals


def setup_routes(config):
    a = config.add_route

    # Public routes
    a('home', '/')
    a('page', '/page/{page:[a-zA-Z0-9_-]+}')

    # Account related
    a('account_redirect', '/account')
    a('account', '/account/')
    a('account_login', '/account/login')
    a('account_logout', '/account/logout')
    a('account_forgot', '/account/forgot')
    a('account_signup', '/account/signup')
    a('order_post', '/order/', request_method='POST')
    a('order_view', '/order/view/{hexid:[a-f0-9]+}')
    a('order_callback', '/order/callback/{hexid:[a-f0-9]+}')
    a('config', '/config/ccrypto.ovpn')
    a('config_profile', '/config/ccrypto-{profile:[a-zA-Z0-9]+}.ovpn')

    # Admin related
    a('admin_home', '/admin/')
    a('admin_graph', '/admin/graph/{name}.svg')
    a('admin_users', '/admin/users')
    a('admin_orders', '/admin/orders')
    a('admin_giftcodes', '/admin/giftcodes')
    a('admin_apiaccess', '/admin/apiaccess')

    # Server API
    a('api_server_auth', '/api/server/auth')
    a('api_server_disconnect', '/api/server/disconnect')
    a('api_server_config', '/api/server/config')


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
    config.include('pyramid_mako')
    config.set_session_factory(session_factory)
    config.add_request_method(get_user, 'user', reify=True, property=True)
    config.add_static_view('static', 'static', cache_max_age=3600)
    setup_routes(config)
    config.scan()

    ca_path = settings.get('openvpn.ca-cert', None)
    if ca_path:
        views.account.ca_content = open(ca_path, 'r').read()
    else:
        views.account.ca_content = ''

    return config.make_wsgi_app()


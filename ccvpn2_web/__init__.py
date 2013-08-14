from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings
from pyramid.authorization import ACLAuthorizationPolicy
from . import views

from .models import (DBSession, Base, User, get_user)

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

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)
    authentication = AuthenticationPolicy()
    authorization = AuthorizationPolicy()
    config = Configurator(settings=settings,
        authentication_policy=authentication, authorization_policy=authorization)
    config.set_session_factory(session_factory)
    config.set_request_property(get_user, 'user', reify=True)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home',           '/')
    config.add_route('account_redirect', '/account')
    config.add_route('account',        '/account/')
    config.add_route('account_login',  '/account/login')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_forgot', '/account/forgot')
    config.add_route('account_signup', '/account/signup')
    config.add_route('order_post',     '/order/', request_method='POST')
    config.add_route('order_view',     '/order/view/{hexid:[a-f0-9]+}')
    config.add_route('order_callback', '/order/callback/{hexid:[a-f0-9]+}')
    config.add_route('page',           '/page/{page:[a-zA-Z0-9_-]+}')
    config.add_route('config',         '/config/ccrypto-{version:[a-z]+}.ovpn')
    config.add_route('config_profile', '/config/ccrypto-{profile:[a-zA-Z0-9]+}-{version:[a-z]+}.ovpn')
    config.add_route('admin_home',     '/admin/')
    config.add_route('admin_users',    '/admin/users')
    config.add_route('admin_orders',   '/admin/orders')
    config.add_route('admin_giftcodes','/admin/giftcodes')
    config.add_route('admin_apiaccess','/admin/apiaccess')
    config.add_route('api_server_auth','/api/server/auth')
    config.add_route('api_server_disconnect','/api/server/disconnect')
    config.add_route('api_server_config','/api/server/config')
    config.scan()

    views.ca_content = open(settings['openvpn.ca-cert'], 'r').read()

    return config.make_wsgi_app()


from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings
from pyramid.authorization import ACLAuthorizationPolicy

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
    config.add_route('account_login',  '/account/login', request_method='POST')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_forgot', '/account/forgot')
    config.add_route('account_signup', '/account/signup')
    config.add_route('page',           '/page/{page:[a-z]+}')
    config.scan()
    return config.make_wsgi_app()


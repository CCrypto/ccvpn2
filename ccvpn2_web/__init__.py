from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings

from .models import (DBSession, Base, User, get_user)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings)
    config.set_session_factory(session_factory)
    config.set_request_property(get_user, 'user', reify=True)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home',           '/')
    config.add_route('account',        '/account')
    config.add_route('account_login',  '/account/login', request_method='POST')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_forgot', '/account/forgot')
    config.add_route('account_signup', '/account/signup')
    config.add_route('page',           '/page/{page:[a-z]+}')
    config.scan()
    return config.make_wsgi_app()


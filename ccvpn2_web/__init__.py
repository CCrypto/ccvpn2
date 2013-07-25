from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home',           '/')
    config.add_route('account',        '/account')
    config.add_route('account_login',  '/account/login')
    config.add_route('account_logout', '/account/logout')
    config.add_route('account_signup', '/account/signup')
    config.add_route('page',           '/page/{page:[a-z]+}')
    config.scan()
    return config.make_wsgi_app()


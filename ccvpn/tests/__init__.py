from pyramid import testing
from sqlalchemy import engine_from_config
from pyramid.i18n import get_localizer, TranslationStringFactory
from paste.deploy.loadwsgi import appconfig
from ccvpn.models import DBSession, Base, get_user
from ccvpn import Messages, referral_handler, methods
import unittest
import os

here = os.path.dirname(__file__)

localtest = os.path.join(here, '../../', 'test.local.ini')
if os.path.isfile(localtest):
    settings = appconfig('config:' + localtest)
else:
    test = os.path.join(here, '../../', 'test.ini')
    settings = appconfig('config:' + test)

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, 'sqlalchemy.')

    def setUp(self):
        if not 'mako.directories' in settings:
            settings['mako.directories'] = 'ccvpn:templates/'
        if not 'mako.imports' in settings:
            settings['mako.imports'] = 'from ccvpn.filters import check'

        self.config = testing.setUp(settings=settings)
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_mako')
        self.config.include('pyramid_beaker')
        self.config.include('pyramid_mailer.testing')
        setup_routes(self.config)

        DBSession.remove()

        #self.engine = engine_from_config(settings, 'sqlalchemy.')
        self.conn = self.engine.connect()
        self.trans = self.conn.begin()

        DBSession.configure(bind=self.conn)
        Base.metadata.create_all(self.engine)
        self.session = DBSession

    def tearDown(self):
        testing.tearDown()
        self.trans.rollback()
        self.session.remove()
        self.conn.close()

class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = Messages(self)
        self.referrer = None
        set
        self.remote_addr = kwargs.get('remote_addr')
        self.translate = TranslationStringFactory('ccvpn')

        methods_objs = {}
        for c in methods.Method.__subclasses__():
            obj = c({})
            methods_objs[c.name] = obj
            methods_objs[c.id] = obj
        self.payment_methods = methods_objs

        referral_handler(self)

    @property
    def user(self):
        return get_user(self)

from ccvpn.tests.filters import *  # noqa
from ccvpn.tests.models import *  # noqa
from ccvpn.tests.scripts import *  # noqa
from ccvpn.tests.views_account import *  # noqa
from ccvpn.tests.views_api import *  # noqa
from ccvpn.tests.views_order import *  # noqa


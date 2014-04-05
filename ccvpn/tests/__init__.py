from pyramid import testing
from sqlalchemy import create_engine

from ccvpn.models import DBSession, Base, get_user
from ccvpn import Messages, referral_handler, methods


def setup_database():
    """ Create an empty database and structure """
    DBSession.remove()
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = Messages(self)
        self.referrer = None
        self.remote_addr = kwargs.get('remote_addr')

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


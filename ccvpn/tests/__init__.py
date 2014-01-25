from pyramid import testing
from sqlalchemy import create_engine

from ccvpn.models import DBSession, Base, get_user
from ccvpn import Messages, get_referrer, referral_handler


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
        referral_handler(self)

    @property
    def user(self):
        return get_user(self)

from ccvpn.tests.filters import *  # noqa
from ccvpn.tests.models import *  # noqa
from ccvpn.tests.scripts import *  # noqa
from ccvpn.tests.views_account import *  # noqa
from ccvpn.tests.views_api import *  # noqa


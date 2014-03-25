import datetime
import unittest
from io import StringIO

import transaction
from webtest import TestApp
from pyramid import testing
from sqlalchemy import create_engine

from ccvpn.models import DBSession, Base, User, Gateway, Profile
from ccvpn import views, main, models, filters
from ccvpn.scripts import initializedb, checkbtcorders, apiacl
from ccvpn.tests import setup_database


class TestScriptInitDB(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)

    def tearDown(self):
        testing.tearDown()
        DBSession.remove()

    def test_usage(self):
        with self.assertRaises(SystemExit):
            initializedb.usage([''], out=StringIO())

    def test_do(self):
        initializedb.initialize_db()

        u = DBSession.query(User).first()
        self.assertIsNotNone(u)


class TestScriptCheckBTCOrders(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        with transaction.manager:
            self.testuser = User(username='test', password='testpw')
            self.session.add(self.testuser)
            self.testorder = models.Order(user=self.testuser.id, amount=2,
                                   method=models.Order.METHOD.BITCOIN,
                                   time=datetime.timedelta(days=30))

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def test_usage(self):
        with self.assertRaises(SystemExit):
            checkbtcorders.usage([''], out=StringIO())


import datetime
import unittest
import transaction
from webtest import TestApp
from pyramid import testing
from sqlalchemy import create_engine

from ccvpn.models import DBSession, Base, User, APIAccessToken, Profile
from ccvpn import views, main, models

def setup_database():
    """ Create an empty database and structure """
    DBSession.remove()
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession

class TestUserPassword(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        with transaction.manager:
            user = User(username='test', password='testpw')
            self.session.add(user)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        user = self.session.query(User).filter_by(username='test').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('testpw'))

class TestUserLoginView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        with transaction.manager:
            user = User(username='test', password='testpw')
            self.session.add(user)
        app = main({})
        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        self.testapp.get('/account/login', status=200)
        res = self.testapp.post('/account/login', {
            'username': 'test',
            'password': 'testpw',
        }, status=303)

class TestAPIAuth(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        with transaction.manager:
            user = User(username='test', password='testpw')
            user.add_paid_time(datetime.timedelta(days=30))
            self.session.add(user)
        with transaction.manager:
            token = APIAccessToken(token='apitoken')
            self.session.add(token)
        
        app = main({})
        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        self.testapp.post('/api/server/auth', {
            'username': 'test',
            'password': 'testpw'
        }, headers={
            'X-API-Token': 'apitoken'
        }, status=200)

class TestAPIDisconnect(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        app = main({})
        self.session = setup_database()
        
        with transaction.manager:
            user = User(username='test', password='testpw')
            user.add_paid_time(datetime.timedelta(days=30))
            self.session.add(user)
        with transaction.manager:
            token = APIAccessToken(token='apitoken')
            self.session.add(token)
        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        resp = self.testapp.post('/api/server/disconnect', {}, headers={
            'X-API-Token': 'apitoken'
        }, status=200)
        self.assertEqual(resp.body, b'')

class TestAPIConfig(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        app = main({})
        self.session = setup_database()
        with transaction.manager:
            user = User(username='test', password='testpw')
            user.add_paid_time(datetime.timedelta(days=30))
            self.session.add(user)
        with transaction.manager:
            token = APIAccessToken(token='apitoken')
            self.session.add(token)
        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        resp = self.testapp.get('/api/server/config', {
            'username': 'test'
        }, headers={
            'X-API-Token': 'apitoken'
        }, status=200)
        self.assertEqual(resp.body, b'')
        
        # With an unknown user
        resp = self.testapp.get('/api/server/config', {
            'username': 'NOTtest'
        }, headers={
            'X-API-Token': 'apitoken'
        }, status=404)

class TestAPIConfigProfile(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        app = main({})
        self.session = setup_database()
        
        with transaction.manager:
            user = User(username='test', password='testpw')
            user.add_paid_time(datetime.timedelta(days=30))
            self.session.add(user)
        self.session.commit()
        with transaction.manager:
            token = APIAccessToken(token='apitoken')
            self.session.add(token)
        with transaction.manager:
            profile = Profile(uid=user.id, name='testprofile')
            self.session.add(profile)
        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        resp = self.testapp.get('/api/server/config', {
            'username': 'test/testprofile'
        }, headers={
            'X-API-Token': 'apitoken'
        }, status=200)
        self.assertEqual(resp.body, b'')

        # With an unknown profile
        resp = self.testapp.get('/api/server/config', {
            'username': 'test/NOTtestprofile'
        }, headers={
            'X-API-Token': 'apitoken'
        }, status=404)



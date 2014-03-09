import datetime
import unittest

import transaction
from pyramid import testing, httpexceptions

from ccvpn.models import User, APIAccessToken, Profile
from ccvpn import views, setup_routes
from ccvpn.tests import setup_database, DummyRequest


class TestAPIViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)
        self.session = setup_database()

        with transaction.manager:
            user = User(username='test', password='testpw')
            user.add_paid_time(datetime.timedelta(days=30))
            self.session.add(user)

            duser = User(username='disabledtest', password='testpw')
            duser.is_active = False
            duser.add_paid_time(datetime.timedelta(days=30))
            self.session.add(duser)

            baduser = User(username='badtest', password='testpw')
            self.session.add(baduser)
        with transaction.manager:
            token = APIAccessToken(token='apitoken')
            self.session.add(token)

            restricted_token = APIAccessToken(token='restricted_apitoken')
            restricted_token.remote_addr = '127.0.0.1'
            self.session.add(restricted_token)
        with transaction.manager:
            profile = Profile(uid=user.id, name='testprofile')
            self.session.add(profile)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_disconnect(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        })
        resp = views.api.api_server_disconnect(req)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.body, b'')

    def test_server_auth(self):
        function = views.api.require_api_token(None)(lambda req: True)

        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        })
        self.assertEqual(function(req), True)

        req = DummyRequest(headers={
            'X-API-Token': 'notapitoken'
        })
        self.assertIsInstance(function(req), httpexceptions.HTTPForbidden)

        req = DummyRequest(headers={
            'X-API-Token': 'restricted_apitoken'
        }, remote_addr='1.2.3.4')
        self.assertIsInstance(function(req), httpexceptions.HTTPUnauthorized)

        req = DummyRequest(headers={
            'X-API-Token': 'restricted_apitoken'
        }, remote_addr='127.0.0.1')
        self.assertEqual(function(req), True)

        req = DummyRequest()
        self.assertIsInstance(function(req), httpexceptions.HTTPBadRequest)

    def test_config(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, params={
            'username': 'test',
        })
        resp = views.api.api_server_config(req)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.body, b'')

    def test_config_with_profile(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, params={
            'username': 'test/testprofile',
        })
        resp = views.api.api_server_config(req)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.body, b'')

    def test_config_no_post(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        })
        resp = views.api.api_server_config(req)
        self.assertEqual(resp.code, 400)

    def test_config_unknown_user(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, params={
            'username': 'nottest',
        })
        resp = views.api.api_server_config(req)
        self.assertEqual(resp.code, 404)

    def test_config_unknown_profile(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, params={
            'username': 'test/nottesttprofile',
        })
        resp = views.api.api_server_config(req)
        self.assertEqual(resp.code, 404)

    def test_user_auth(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'test',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 200)

    def test_user_auth_disabled(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'disabledtest',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 403)

    def test_user_auth_profile(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'test/testprofile',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 200)

    def test_user_auth_no_post(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 400)

    def test_user_auth_unknown_user(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'nottest',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 403)

    def test_user_auth_unknown_profile(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'test/nottestprofile',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 403)

    def test_user_auth_expired(self):
        req = DummyRequest(headers={
            'X-API-Token': 'apitoken'
        }, post={
            'username': 'badtest',
            'password': 'testpw'
        })
        resp = views.api.api_server_auth(req)
        self.assertEqual(resp.code, 401)


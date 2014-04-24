import datetime
import unittest

import transaction
from pyramid import testing, httpexceptions

from ccvpn.models import User, Gateway, Profile, VPNSession
from ccvpn import views, setup_routes
from ccvpn.tests import setup_database, DummyRequest


class TestAPIViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)
        self.session = setup_database()

        self.paiduser = User(username='paiduser', password='testpw')
        self.paiduser.add_paid_time(datetime.timedelta(days=30))
        self.session.add(self.paiduser)
        self.session.flush()

        self.profile = Profile(uid=self.paiduser.id, name='testprofile')
        self.session.add(self.profile)

        self.freeuser = User(username='freeuser', password='testpw')
        self.session.add(self.freeuser)

        duser = User(username='disableduser', password='testpw')
        duser.is_active = False
        duser.add_paid_time(datetime.timedelta(days=30))
        self.session.add(duser)

        self.gw0 = Gateway(name='gw0', token='simple_gateway',
                      isp_name='', isp_url='', country='')
        self.session.add(self.gw0)

        self.gw1 = Gateway(name='gw1', token='disabled_gateway',
                      isp_name='', isp_url='', country='')
        self.gw1.enabled = False
        self.session.add(self.gw1)

        self.gw2 = Gateway(name='gw2', token='ipv4_gateway',
                      isp_name='', isp_url='', country='',
                      ipv4='1.2.3.4')
        self.session.add(self.gw2)

        self.gw3 = Gateway(name='gw3', token='ipv6_gateway',
                      isp_name='', isp_url='', country='',
                      ipv6='1:2:3:4:5:6:7:8')
        self.session.add(self.gw3)
        self.session.flush()

        self.testheaders = {
            'X-Gateway-Token': 'simple_gateway',
            'X-Gateway-Version': 'alpha',
        }

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def assertSessionExists(self, **kwargs):
        sess = self.session.query(VPNSession)
        sess = sess.filter_by(**kwargs)
        sess = sess.all()
        self.assertGreaterEqual(len(sess), 1,
                                msg='No session found for ' + str(kwargs))

    def assertNSessionExists(self, n, **kwargs):
        sess = self.session.query(VPNSession)
        sess = sess.filter_by(**kwargs)
        sess = sess.all()
        msg = '%d != %d sessions found for %s' % (len(sess), n, str(kwargs))
        self.assertEqual(len(sess), n, msg=msg)

    def test_api_auth(self):
        fn = views.api.require_api_token(None)(lambda req: True)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'simple_gateway',
            'X-Gateway-Version': 'alpha',
        })
        self.assertEqual(fn(req), True)

        # Invalid or missing headers
        req = DummyRequest(headers={
            'X-Gateway-Token': 'simple_gateway',
            'X-Gateway-Version': 'something_else',
        })
        self.assertIsInstance(fn(req), httpexceptions.HTTPBadRequest)

        req = DummyRequest(headers={
            'X-Gateway-Version': 'alpha',
        })
        self.assertIsInstance(fn(req), httpexceptions.HTTPBadRequest)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'simple_gateway',
        })
        self.assertIsInstance(fn(req), httpexceptions.HTTPBadRequest)

        # Invalid header content
        req = DummyRequest(headers={
            'X-Gateway-Token': 'unknown_gateway',
            'X-Gateway-Version': 'alpha',
        })
        self.assertIsInstance(fn(req), httpexceptions.HTTPForbidden)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'disabled_gateway',
            'X-Gateway-Version': 'alpha',
        })
        self.assertIsInstance(fn(req), httpexceptions.HTTPForbidden)

        # Invalid source address
        req = DummyRequest(headers={
            'X-Gateway-Token': 'ipv4_gateway',
            'X-Gateway-Version': 'alpha',
        }, remote_addr='1.2.3.4')
        self.assertEqual(fn(req), True)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'ipv4_gateway',
            'X-Gateway-Version': 'alpha',
        }, remote_addr='4.3.2.1')
        self.assertIsInstance(fn(req), httpexceptions.HTTPForbidden)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'ipv6_gateway',
            'X-Gateway-Version': 'alpha',
        }, remote_addr='1:2:3:4:5:6:7:8')
        self.assertEqual(fn(req), True)

        req = DummyRequest(headers={
            'X-Gateway-Token': 'ipv6_gateway',
            'X-Gateway-Version': 'alpha',
        }, remote_addr='8:7:6:5:4:3:2:1')
        self.assertIsInstance(fn(req), httpexceptions.HTTPForbidden)


    def test_auth(self):
        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
            'password': 'testpw',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'freeuser',
            'password': 'testpw',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'disableduser',
            'password': 'testpw',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/testprofile',
            'password': 'testpw',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/NOTtestprofile',
            'password': 'testpw',
        })
        resp = views.api.api_gateway_auth(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)
        self.assertEqual(resp.body, b'')

    def test_connect(self):
        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
            'remote_addr': '1.2.3.4',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertSessionExists(user_id=self.paiduser.id, disconnect_date=None)

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/testprofile',
            'remote_addr': '1.2.3.4',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/NOTtestprofile',
            'remote_addr': '1.2.3.4',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'remote_addr': '',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'freeuser',
            'remote_addr': '',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)
        self.assertEqual(resp.body, b'')

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'disableduser',
            'remote_addr': '',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPForbidden)
        self.assertEqual(resp.body, b'')

    def test_disconnect_one(self):
        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/testprofile',
            'remote_addr': '1.2.3.4',
        })
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertNSessionExists(1, user_id=self.paiduser.id, disconnect_date=None)

        # Missing POST data
        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/testprofile',
        })
        resp = views.api.api_gateway_disconnect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)
        self.assertNSessionExists(1, user_id=self.paiduser.id, disconnect_date=None)

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser/testprofile',
            'bytes_up': 1337,
            'bytes_down': 42,
        })
        resp = views.api.api_gateway_disconnect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertNSessionExists(0, user_id=self.paiduser.id, disconnect_date=None)

    def test_disconnect_multiple(self):
        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
            'remote_addr': '1.2.3.4',
        })
        resp = views.api.api_gateway_connect(req)
        resp = views.api.api_gateway_connect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertNSessionExists(2, user_id=self.paiduser.id, disconnect_date=None)

        req = DummyRequest(headers=self.testheaders, post={
            'username': 'paiduser',
            'bytes_up': 0,
            'bytes_down': 0,
        })
        resp = views.api.api_gateway_disconnect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPOk)
        self.assertNSessionExists(0, user_id=self.paiduser.id, disconnect_date=None)


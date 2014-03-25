import datetime
import unittest

import transaction
from pyramid import testing, httpexceptions

from ccvpn.models import User, Gateway, Profile
from ccvpn import views, setup_routes
from ccvpn.tests import setup_database, DummyRequest


class TestAPIViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)
        self.session = setup_database()

        with transaction.manager:
            paiduser = User(username='paiduser', password='testpw')
            paiduser.add_paid_time(datetime.timedelta(days=30))
            self.session.add(paiduser)

            freeuser = User(username='freeuser', password='testpw')
            self.session.add(freeuser)

            duser = User(username='disableduser', password='testpw')
            duser.is_active = False
            duser.add_paid_time(datetime.timedelta(days=30))
            self.session.add(duser)

        with transaction.manager:
            gw0 = Gateway(name='gw0', token='simple_gateway',
                          isp_name='', isp_url='', country='')
            self.session.add(gw0)

            gw1 = Gateway(name='gw1', token='disabled_gateway',
                          isp_name='', isp_url='', country='')
            gw1.enabled = False
            self.session.add(gw1)

            gw2 = Gateway(name='gw2', token='ipv4_gateway',
                          isp_name='', isp_url='', country='',
                          ipv4='1.2.3.4')
            self.session.add(gw2)

            gw3 = Gateway(name='gw3', token='ipv6_gateway',
                          isp_name='', isp_url='', country='',
                          ipv6='1:2:3:4:5:6:7:8')
            self.session.add(gw3)

        with transaction.manager:
            profile = Profile(uid=paiduser.id, name='testprofile')
            self.session.add(profile)

        self.testheaders = {
            'X-Gateway-Token': 'simple_gateway',
            'X-Gateway-Version': 'alpha',
        }

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

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



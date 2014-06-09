import datetime
import unittest

from pyramid import testing
from pyramid import httpexceptions

from ccvpn.models import User, Order, GiftCode
from ccvpn import views, setup_routes
from ccvpn.tests import BaseTest, DummyRequest


class TestOrderView(BaseTest):
    def setUp(self):
        super().setUp()

        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.testadmin = User(username='testadmin', password='testpw')
        self.testadmin.is_admin = True
        self.session.add(self.testadmin)
        self.session.flush()
        self.testcode = GiftCode(datetime.timedelta(days=7))
        self.session.add(self.testcode)
        self.session.flush()

    def test_post_code(self):
        req = DummyRequest(post={'code': self.testcode.code})
        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertTrue(self.testuser.is_paid)
        until = self.testuser.paid_until

        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertTrue(self.testuser.is_paid)
        self.assertEquals(self.testuser.paid_until, until)

    def test_post_admin(self):
        req = DummyRequest(post={'method': 'admin', 'time': '3'})

        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)
        self.assertFalse(self.testuser.is_paid)

        req = DummyRequest(post={'method': 'admin', 'time': '3'})
        req.session['uid'] = self.testadmin.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertTrue(self.testadmin.is_paid)

    def test_post_unknown_code(self):
        req = DummyRequest(post={'code': 'fail'})
        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertFalse(self.testuser.is_paid)

    def test_post_order_paypal(self):
        req = DummyRequest(post={
            'method': 'paypal',
            'time': '1'
        })
        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertIn('paypal.com', resp.location)

    def test_post_order_paypal_invalid_method(self):
        req = DummyRequest(post={
            'method': 'dogecoin',
            'time': '1'
        })
        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)

    def test_post_order_paypal_invalid_time(self):
        req = DummyRequest(post={
            'method': 'paypal',
            'time': 'one'
        })
        req.session['uid'] = self.testuser.id
        resp = views.order.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)

    def test_view_paypal(self):
        testorder = Order(user=self.testuser.id, amount=1,
                          method=Order.METHOD.PAYPAL,
                          time=datetime.timedelta(days=30))
        self.session.add(testorder)
        self.session.flush()

        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % testorder.id
        resp = views.order.order_view(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['o'], testorder)

    def test_view_btc(self):
        testorder = Order(user=self.testuser.id, amount=1,
                          method=Order.METHOD.BITCOIN,
                          time=datetime.timedelta(days=30))
        testorder.payment = {'btc_address': 'TESTADDRESS'}
        self.session.add(testorder)
        self.session.flush()

        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % testorder.id
        resp = views.order.order_view(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['o'], testorder)

    def test_view_not_found(self):
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % 4242
        resp = views.order.order_view(req)
        self.assertIsInstance(resp, httpexceptions.HTTPNotFound)

    def test_view_not_owned(self):
        otheruser = User(username='othertest', password='testpw')
        self.session.add(otheruser)
        self.session.flush()

        testorder = Order(user=otheruser.id, amount=1,
                          method=Order.METHOD.PAYPAL,
                          time=datetime.timedelta(days=30))
        self.session.add(testorder)
        self.session.flush()

        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % testorder.id
        resp = views.order.order_view(req)
        self.assertIsInstance(resp, httpexceptions.HTTPUnauthorized)



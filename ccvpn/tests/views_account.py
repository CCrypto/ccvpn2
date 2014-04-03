import datetime
import unittest

import transaction
from pyramid import testing
from pyramid_mailer import get_mailer
from pyramid import httpexceptions

from ccvpn.models import User, Order, Profile, PasswordResetToken, GiftCode
from ccvpn import views, setup_routes
from ccvpn.tests import setup_database, DummyRequest


class TestPublicViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)

    def tearDown(self):
        testing.tearDown()

    def test_page(self):
        req = DummyRequest()
        req.matchdict['page'] = 'help'
        resp = views.page(req)
        self.assertIsInstance(resp, dict)
        self.assertIn('Installation guides:', resp['content'])

    def test_page_fail(self):
        req = DummyRequest()
        req.matchdict['page'] = 'does-not-exists'
        resp = views.page(req)
        self.assertIsInstance(resp, httpexceptions.HTTPNotFound)

    def test_home(self):
        req = DummyRequest()
        resp = views.home(req)
        self.assertIsInstance(resp, dict)

    def test_account_redirect(self):
        req = DummyRequest()
        resp = views.account.account_redirect(req)
        self.assertIsInstance(resp, httpexceptions.HTTPMovedPermanently)
        self.assertTrue(resp.location.endswith('/account/'))


class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)
        self.session = setup_database()
        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.session.flush()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_login_form(self):
        req = DummyRequest()
        resp = views.account.login(req)
        self.assertIsInstance(resp, dict)

    def test_login(self):
        req = DummyRequest(post={
            'username': 'test',
            'password': 'testpw',
        })
        resp = views.account.login(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertEqual(req.session['uid'], self.testuser.id)

    def test_login_invalid_password(self):
        req = DummyRequest(post={
            'username': 'test',
            'password': 'nottestpw',
        })
        resp = views.account.login(req)
        self.assertIsInstance(resp, dict)
        self.assertNotEqual(req.session.get('uid'), self.testuser.id)

    def test_login_invalid_req(self):
        req = DummyRequest(post={})
        resp = views.account.login(req)
        self.assertIsInstance(resp, dict)
        self.assertNotEqual(req.session.get('uid'), self.testuser.id)

    def test_logout(self):
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        resp = views.account.logout(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertNotEqual(req.session.get('uid'), self.testuser.id)

    def test_account_page(self):
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        resp = views.account.account(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 200)


class TestSignupView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        setup_routes(self.config)
        self.session = setup_database()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def user_exists(self, name):
        u = self.session.query(User.id).filter_by(username=name).first()
        return u is not None

    def test_form(self):
        req = DummyRequest()
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)

    def test_valid(self):
        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'email@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))

    def test_valid_referral(self):
        with transaction.manager:
            _referrer = User(username='test', password='testpw')
            self.session.add(_referrer)

        referrer = self.session.query(User).filter_by(username='test').first()
        self.assertFalse(referrer.is_paid)

        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'email@host'
        }, params={
            'ref': str(referrer.id),
        })
        resp = views.account.signup(req)

        newuser = self.session.query(User).filter_by(username='newtest').first()
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertEqual(newuser.referrer_id, referrer.id)

        self.assertFalse(referrer.is_paid)

        testorder = Order(user=newuser, amount=1,
                          method=Order.METHOD.BITCOIN,
                          time=datetime.timedelta(days=30))
        self.session.add(testorder)
        self.session.add(referrer)
        self.session.flush()
        testorder.close(force=True)
        self.session.flush()

        self.session.refresh(referrer)
        self.assertTrue(referrer.is_paid)

    def test_invalid_username(self):
        req = DummyRequest(post={
            'username': 'newtest!',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'email@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)
        self.assertFalse(self.user_exists('newtest'))

    def test_invalid_password(self):
        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'a' * 1024,
            'password2': 'a' * 1024,
            'email': 'email@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)
        self.assertFalse(self.user_exists('newtest'))

    def test_invalid_password2(self):
        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'newpw',
            'password2': 'i\'m different',
            'email': 'email@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)
        self.assertFalse(self.user_exists('newtest'))

    def test_invalid_email(self):
        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'email host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)
        self.assertFalse(self.user_exists('newtest'))

    def test_existing_username(self):
        with transaction.manager:
            u = User(username='newtest', email='user@host', password='newpw')
            self.session.add(u)
        req = DummyRequest(post={
            'username': 'newtest',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'user2@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)

    def test_existing_email(self):
        with transaction.manager:
            u = User(username='newtest', email='user@host', password='newpw')
            self.session.add(u)
        req = DummyRequest(post={
            'username': 'newtest2',
            'password': 'newpw',
            'password2': 'newpw',
            'email': 'user@host'
        })
        resp = views.account.signup(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(req.response.status_code, 400)


class TestForgotView(unittest.TestCase):
    def setUp(self):
        settings = {
            'mail.default_sender': 'root@lo',
            'mako.directories': 'ccvpn:templates/'
        }
        self.config = testing.setUp(settings=settings)
        setup_routes(self.config)
        self.config.include('pyramid_mailer.testing')
        self.session = setup_database()

        with transaction.manager:
            testuser = User(username='test', password='testpw',
                            email='user@host')
            self.session.add(testuser)
            testuserw = User(username='testWOemail', password='testpw')
            self.session.add(testuserw)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_form(self):
        req = DummyRequest()
        resp = views.account.forgot(req)
        self.assertEqual(req.response.status_code, 200)
        self.assertIsInstance(resp, dict)

        req = DummyRequest(post={})
        resp = views.account.forgot(req)
        self.assertEqual(req.response.status_code, 200)
        self.assertIsInstance(resp, dict)

    def test_valid(self):
        req = DummyRequest(post={
            'username': 'test',
        })
        req.remote_addr = '127.0.0.1'
        resp = views.account.forgot(req)
        self.assertEqual(req.response.status_code, 200)
        self.assertIsInstance(resp, dict)

        registry = self.config.registry
        mailer = get_mailer(registry)
        self.assertEqual(len(mailer.outbox), 1)

    def test_invalid_username(self):
        req = DummyRequest(post={
            'username': 'NOTtest',
        })
        req.remote_addr = '127.0.0.1'
        resp = views.account.forgot(req)
        self.assertEqual(req.response.status_code, 400)
        self.assertIsInstance(resp, dict)

    def test_invalid_email(self):
        req = DummyRequest(post={
            'username': 'testWOemail',
        })
        req.remote_addr = '127.0.0.1'
        resp = views.account.forgot(req)
        self.assertEqual(req.response.status_code, 400)
        self.assertIsInstance(resp, dict)


class TestResetView(unittest.TestCase):
    def setUp(self):
        settings = {
            'mail.default_sender': 'root@lo',
            'mako.directories': 'ccvpn:templates/'
        }
        self.config = testing.setUp(settings=settings)
        setup_routes(self.config)
        self.config.include('pyramid_mailer.testing')
        self.session = setup_database()

        testuser = User(username='test', password='testpw',
                        email='user@host')
        self.session.add(testuser)
        self.session.flush()
        self.token = PasswordResetToken(uid=testuser.id)
        self.session.add(self.token)
        self.session.flush()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_invalid_token(self):
        req = DummyRequest()
        req.matchdict['token'] = 'invalidtoken'
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertIsInstance(resp, httpexceptions.HTTPMovedPermanently)

    def test_form(self):
        req = DummyRequest()
        req.matchdict['token'] = self.token.token
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertEqual(req.response.status_code, 200)
        self.assertIsInstance(resp, dict)

        req = DummyRequest(post={})
        req.matchdict['token'] = self.token.token
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertEqual(req.response.status_code, 200)
        self.assertIsInstance(resp, dict)

    def test_invalid_password(self):
        req = DummyRequest(post={
            'password': 'pw',
            'password2': 'notpw'
        })
        req.matchdict['token'] = self.token.token
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertEqual(req.response.status_code, 400)
        self.assertIsInstance(resp, dict)

    def test_valid(self):
        req = DummyRequest(post={
            'password': 'newpw',
            'password2': 'newpw',
        })
        req.matchdict['token'] = self.token.token
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertIsInstance(resp, httpexceptions.HTTPMovedPermanently)
        self.assertTrue(resp.location.endswith('/account/login'))

        registry = self.config.registry
        mailer = get_mailer(registry)
        self.assertEqual(len(mailer.outbox), 1)

        # Should not be able to use a token > 1 time
        req = DummyRequest(post={
            'password': 'newpw',
            'password2': 'newpw',
        })
        req.matchdict['token'] = self.token.token
        req.remote_addr = '127.0.0.1'
        resp = views.account.reset(req)
        self.assertIsInstance(resp, httpexceptions.HTTPMovedPermanently)
        self.assertTrue(resp.location.endswith('/account/forgot'))

        registry = self.config.registry
        mailer = get_mailer(registry)
        self.assertEqual(len(mailer.outbox), 1)


class TestOrderView(unittest.TestCase):
    def setUp(self):
        settings = {
            'mako.directories': 'ccvpn:templates/'
        }
        self.config = testing.setUp(settings=settings)
        setup_routes(self.config)
        self.session = setup_database()

        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.session.flush()
        self.testcode = GiftCode(datetime.timedelta(days=7))
        self.session.add(self.testcode)
        self.session.flush()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_post_code(self):
        req = DummyRequest(post={'code': self.testcode.code})
        req.session['uid'] = self.testuser.id
        resp = views.account.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertTrue(self.testuser.is_paid)

    def test_post_unknown_code(self):
        req = DummyRequest(post={'code': 'fail'})
        req.session['uid'] = self.testuser.id
        resp = views.account.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertTrue(resp.location.endswith('/account/'))
        self.assertFalse(self.testuser.is_paid)

    def test_post_order_paypal(self):
        req = DummyRequest(post={
            'method': 'paypal',
            'time': '1'
        })
        req.session['uid'] = self.testuser.id
        resp = views.account.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPSeeOther)
        self.assertIn('paypal.com', resp.location)

    def test_post_order_paypal_invalid_method(self):
        req = DummyRequest(post={
            'method': 'dogecoin',
            'time': '1'
        })
        req.session['uid'] = self.testuser.id
        resp = views.account.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)

    def test_post_order_paypal_invalid_time(self):
        req = DummyRequest(post={
            'method': 'paypal',
            'time': 'one'
        })
        req.session['uid'] = self.testuser.id
        resp = views.account.order_post(req)
        self.assertIsInstance(resp, httpexceptions.HTTPBadRequest)

    def test_view_paypal(self):
        testorder = Order(user=self.testuser.id, amount=1,
                          method=Order.METHOD.PAYPAL,
                          time=datetime.timedelta(days=30))
        self.session.add(testorder)
        self.session.flush()

        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % testorder.id
        resp = views.account.order_view(req)
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
        resp = views.account.order_view(req)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['o'], testorder)

    def test_view_not_found(self):
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['hexid'] = '%x' % 4242
        resp = views.account.order_view(req)
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
        resp = views.account.order_view(req)
        self.assertIsInstance(resp, httpexceptions.HTTPUnauthorized)


class TestConfigView(unittest.TestCase):
    def setUp(self):
        settings = {
            'mako.directories': 'ccvpn:templates/'
        }
        self.config = testing.setUp(settings=settings)
        setup_routes(self.config)
        self.session = setup_database()

        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.session.flush()
        profile = Profile(uid=self.testuser.id, name='testprofile')
        self.session.add(profile)
        self.session.flush()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_get(self):
        gw = bytes(views.account.openvpn_gateway, 'ascii')
        ca = bytes(views.account.openvpn_ca, 'ascii')
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        resp = views.account.config(req)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(gw, resp.body)
        self.assertIn(ca, resp.body)

    def test_profile(self):
        gw = bytes(views.account.openvpn_gateway, 'ascii')
        ca = bytes(views.account.openvpn_ca, 'ascii')
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.matchdict['profile'] = 'testprofile'
        resp = views.account.config(req)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(gw, resp.body)
        self.assertIn(ca, resp.body)

    def test_unknown_profile(self):
        req = DummyRequest()
        req.session['uid'] = self.testuser.id
        req.GET['profile'] = 'nottestprofile'
        resp = views.account.config(req)
        self.assertEqual(resp.status_code, 404)


import datetime
import unittest

import transaction
from pyramid import testing

from ccvpn.models import DBSession, User, GiftCode
from ccvpn import models
from ccvpn.tests import setup_database


class TestModelsRandom(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_access_token(self):
        t1 = models.random_access_token()
        t2 = models.random_access_token()
        self.assertEqual(32, len(t1))
        self.assertEqual(len(t1), len(t2))
        self.assertNotEqual(t1, t2)

    def test_gift_code(self):
        t1 = models.random_gift_code()
        t2 = models.random_gift_code()
        self.assertEqual(16, len(t1))
        self.assertEqual(len(t1), len(t2))
        self.assertNotEqual(t1, t2)

    def test_bytes(self):
        length = 42
        t1 = models.random_bytes(length)
        t2 = models.random_bytes(length)
        self.assertEqual(length, len(t1))
        self.assertEqual(len(t1), len(t2))
        self.assertNotEqual(t1, t2)


class TestJSONEncodedDict(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_bind(self):
        import json

        d = ''
        data = {'a': 1, 'b': 2}
        expected = json.dumps(data)

        dic = models.JSONEncodedDict()
        self.assertIsNone(dic.process_bind_param(None, d))
        self.assertEqual(dic.process_bind_param(data, d), expected)

    def test_result(self):
        import json

        d = ''
        expected = {'a': 1, 'b': 2}
        data = json.dumps(expected)

        dic = models.JSONEncodedDict()
        self.assertEqual(dic.process_result_value(None, d), {})
        self.assertEqual(dic.process_result_value(data, d), expected)


class TestGetUser(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.session.flush()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test(self):
        req = testing.DummyRequest()
        self.assertIsNone(models.get_user(req))

        req.session['uid'] = 42
        self.assertIsNone(models.get_user(req))

        req.session['uid'] = self.testuser.id
        self.assertIsInstance(models.get_user(req), User)


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_construct(self):
        user = User(username='test', password='pw')
        self.assertEqual(user.username, 'test')

        self.assertTrue(user.check_password('pw'))
        self.assertFalse(user.check_password('!pw'))

    def test_password(self):
        user = User()
        self.assertFalse(user.check_password(''))
        user.set_password('pw')
        self.assertTrue(user.check_password('pw'))
        self.assertFalse(user.check_password('!pw'))

    def test_paid(self):
        user = User()
        self.assertFalse(user.is_paid)
        self.assertEqual(user.paid_days_left(), 0)

        user.add_paid_time(datetime.timedelta(days=1))
        self.assertTrue(user.is_paid)
        self.assertEqual(user.paid_days_left(), 1)

        user.paid_until = datetime.datetime.fromtimestamp(1)
        user.add_paid_time(datetime.timedelta(days=1))
        self.assertTrue(user.is_paid)
        self.assertEqual(user.paid_days_left(), 1)

    def test_str(self):
        user = User(username='test')
        self.assertEqual(user.username, str(user))

    def test_validation(self):
        self.assertTrue(User.validate_username('username'))
        self.assertFalse(User.validate_username('username/'))
        self.assertFalse(User.validate_username(''))
        self.assertFalse(User.validate_username(None))

        self.assertTrue(User.validate_email('user@host'))
        self.assertFalse(User.validate_email('user host'))
        self.assertFalse(User.validate_email(''))
        self.assertFalse(User.validate_email(None))

        self.assertTrue(User.validate_password('password'))
        self.assertFalse(User.validate_password(''))
        self.assertFalse(User.validate_password(None))


class TestGiftCodeModel(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        self.u = User(username='freeuser', password='a')
        DBSession.add(self.u)
        self.session.flush()

        self.pu = User(username='paiduser', password='a')
        self.pu.add_paid_time(datetime.timedelta(days=30))
        DBSession.add(self.pu)
        self.session.flush()

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def test_username_if_used(self):
        gc = GiftCode()
        self.assertIs(gc.username_if_used, False)
        gc.used = self.u.id
        gc.user = self.u
        self.assertEqual(gc.username_if_used, self.u.username)

    def test_use_freeonly(self):
        gc = GiftCode()
        gc.free_only = True
        self.assertRaises(models.AlreadyUsedGiftCode, gc.use, self.pu)
        gc.use(self.u)
        self.assertTrue(self.u.is_paid)

    def test_use_reuse(self):
        time = datetime.timedelta(days=30, hours=11)
        gc = GiftCode(time=time)
        gc.use(self.u)
        self.assertEqual(self.u.paid_time_left.days, time.days)
        self.assertRaises(models.AlreadyUsedGiftCode, gc.use, self.u)
        self.assertEqual(self.u.paid_time_left.days, time.days)
        gc.use(self.u, reuse=True)
        self.assertTrue(self.u.is_paid)
        self.assertEqual(self.u.paid_time_left.days, time.days*2)


class TestUserModelWithDB(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = setup_database()
        u = User(username='test', email='test@host', password='a')
        DBSession.add(u)
        self.session.flush()

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def test_is_used(self):
        r = User.is_used('test', 'test@host')
        self.assertGreater(r[0], 0)
        self.assertGreater(r[1], 0)


class TestPasswordResetTokenModel(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_construct(self):
        prt = models.PasswordResetToken(42)
        self.assertEqual(prt.uid, 42)
        self.assertIsNotNone(prt.uid)
        self.assertGreater(prt.expire_date, datetime.datetime.now())
        self.assertIsNotNone(prt.token)

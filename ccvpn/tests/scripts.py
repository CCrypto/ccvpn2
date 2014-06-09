from datetime import datetime, timedelta
import unittest
from io import StringIO

from webtest import TestApp
from pyramid import testing
from sqlalchemy import create_engine
from pyramid_mailer import get_mailer

from ccvpn.models import Base, User, Gateway, Profile
from ccvpn import views, main, models, filters
from ccvpn.scripts import initializedb, checkbtcorders, apiacl, expire_mail
from ccvpn.tests import BaseTest


class TestScriptInitDB(BaseTest):
    def test_usage(self):
        with self.assertRaises(SystemExit):
            initializedb.usage([''], out=StringIO())

    def test_do(self):
        initializedb.initialize_db()

        u = self.session.query(User).first()
        self.assertIsNotNone(u)


class TestScriptCheckBTCOrders(BaseTest):
    def setUp(self):
        super().setUp()
        self.testuser = User(username='test', password='testpw')
        self.session.add(self.testuser)
        self.testorder = models.Order(user=self.testuser.id, amount=2,
                               method=models.Order.METHOD.BITCOIN,
                               time=timedelta(days=30))

    def test_usage(self):
        with self.assertRaises(SystemExit):
            checkbtcorders.usage([''], out=StringIO())


class TestScriptExpireMail(BaseTest):
    days = 7

    def setUp(self):
        super().setUp()

    def test_future(self):
        days = 7


        u_exp5 = User(username='exp5', password='.', email='.')
        u_exp5.add_paid_time(timedelta(days=5))
        self.session.add(u_exp5)

        u_exp10 = User(username='exp10', password='.', email='.')
        u_exp10.add_paid_time(timedelta(days=10))
        self.session.add(u_exp10)

        # Same, with last_expiry_notice
        u_exp5l = User(username='exp5l', password='.', email='.')
        u_exp5l.last_expiry_notice = datetime.now() - timedelta(days=1)
        u_exp5l.add_paid_time(timedelta(days=5))
        self.session.add(u_exp5l)

        u_exp5ll = User(username='exp5ll', password='.', email='.')
        u_exp5ll.last_expiry_notice = datetime.now() - timedelta(days=30)
        u_exp5ll.add_paid_time(timedelta(days=5))
        self.session.add(u_exp5ll)

        u_exp5 = self.session.query(User).filter_by(username='exp5').one()
        u_exp10 = self.session.query(User).filter_by(username='exp10').one()
        u_exp5l = self.session.query(User).filter_by(username='exp5l').one()
        u_exp5ll = self.session.query(User).filter_by(username='exp5ll').one()

        users = expire_mail.get_future_expire(days)
        self.assertIn(u_exp5, users)
        self.assertNotIn(u_exp10, users)
        self.assertNotIn(u_exp5l, users)
        self.assertIn(u_exp5ll, users)

    def test_expired(self):
        u_exp = User(username='exp', password='.', email='.',
                   paid_until=datetime.now()-timedelta(days=5))
        u_expl = User(username='expl', password='.', email='.',
                   paid_until=datetime.now()-timedelta(days=5),
                   last_expiry_notice=datetime.now()-timedelta(days=12))
        u_expll = User(username='expll', password='.', email='.',
                   paid_until=datetime.now()-timedelta(days=5),
                   last_expiry_notice=datetime.now()-timedelta(days=1))
        u_expf = User(username='expf', password='.', email='.',
                   paid_until=datetime.now()+timedelta(days=5))
        self.session.add_all([u_exp, u_expl, u_expll, u_expf])

        u_exp = self.session.query(User).filter_by(username='exp').one()
        u_expl = self.session.query(User).filter_by(username='expl').one()
        u_expll = self.session.query(User).filter_by(username='expll').one()
        u_expf = self.session.query(User).filter_by(username='expf').one()

        users = expire_mail.get_expired()
        self.assertIn(u_exp, users)
        self.assertIn(u_expl, users)
        self.assertNotIn(u_expll, users)
        self.assertNotIn(u_expf, users)

    def test_send(self):
        registry = self.config.registry
        mailer = get_mailer(registry)

        u = User(username='test_user_1', email='test1@example.com',
                 paid_until=datetime.now()+timedelta(days=4))
        expire_mail.send_notice(u, mailer)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertIn('test_user_1', mailer.outbox[0].body)
        self.assertIn('test1@example.com', mailer.outbox[0].recipients)

        u = User(username='test_user_2', email='test2@example.com',
                 paid_until=datetime.now()+timedelta(days=-4))
        expire_mail.send_notice(u, mailer)
        self.assertEqual(len(mailer.outbox), 2)
        self.assertIn('test_user_2', mailer.outbox[1].body)
        self.assertIn('test2@example.com', mailer.outbox[1].recipients)




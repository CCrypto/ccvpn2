from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import logging

log = logging.getLogger(__name__)

ext = ZopeTransactionExtension(keep_session=False)
DBSession = scoped_session(sessionmaker(extension=ext))


class Base(object):
    @classmethod
    def one(cls, **kwargs):
        return DBSession.query(cls).filter_by(**kwargs).one()

    @classmethod
    def all(cls, **kwargs):
        return DBSession.query(cls).filter_by(**kwargs).all()


Base = declarative_base(cls=Base)


#!/usr/bin/env python3
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'pyramid_mako',
    'pyramid_mailer',
    'zope.sqlalchemy',
    'waitress',
    'markdown',
    'bitcoin-python',
    'webtest',
    'requests',
    'python-dateutil',
    'stripe',
    'pygments',
    'Babel',
    'lingua',
]

setup(name='ccvpn',
      version='0.0',
      description='ccvpn',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='ccvpn',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ccvpn:main
      [console_scripts]
      initialize_ccvpn_db = ccvpn.scripts.initializedb:main
      ccvpn_checkbtcorders = ccvpn.scripts.checkbtcorders:main
      ccvpn_apiacl = ccvpn.scripts.apiacl:main
      ccvpn_mail = ccvpn.scripts.mail:main
      """,
      message_extractors = { '.': [
          ('**.py', 'python', None ),
          ('**.mako', 'mako', None ),
      ]},
      )

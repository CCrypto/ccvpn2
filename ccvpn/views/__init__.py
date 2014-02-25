import codecs
import markdown
import os
import requests
import json
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPNotFound
from beaker import cache

logger = logging.getLogger(__name__)

from ccvpn.views import account, admin, api  # noqa


@view_config(route_name='home', renderer='home.mako')
def home(request):
    settings = request.registry.settings
    return {
        'eur_price': float(settings.get('paypal.month_price', 2)),
        'btc_price': float(settings.get('bitcoin.month_price', 0.02))
    }


@view_config(route_name='ca_crt')
def ca_crt(request):
    return HTTPOk(body=account.openvpn_ca)


@view_config(route_name='page', renderer='page.mako')
def page(request):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    page = 'pages/' + request.matchdict['page'] + '.md'
    path = os.path.join(root, page)
    try:
        f = codecs.open(path, mode="r", encoding="utf-8")
        content = markdown.markdown(f.read(), extensions=['toc'])
        f.close()
        return {'content': content}
    except FileNotFoundError:
        return HTTPNotFound()


from ccvpn.models import IcingaError, IcingaQuery

@cache.cache_region('short_term')
def get_uptime(request, l):
    settings = request.registry.settings
    base = settings.get('nagios.url')
    user = settings.get('nagios.user')
    password = settings.get('nagios.password')
    r = IcingaQuery(base, (user, password))
    for host in l.keys():
        try:
            l[host]['uptime'] = r.get_uptime(host)
        except IcingaError as e:
            l[host]['uptime'] = '[error]'
            logger.error('Icinga: %s', e.args[0])
    return l

@view_config(route_name='gateways', renderer='gateways.mako')
def gateways(request):
    l = {
        'teta.fr.204vpn.net': {
            'isp': ('Tetaneutral', 'http://tetaneutral.net/'),
            'loc': 'Toulouse, FR',
        },
        'tilaa.nl.204vpn.net': {
            'isp': ('Tilaa', 'https://www.tilaa.com/'),
            'loc': 'Haarlem, NL',
        },
    }
    l = get_uptime(request, l)
    return {'gateways': l}


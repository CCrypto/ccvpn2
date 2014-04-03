import codecs
import markdown
import os
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPNotFound
from sqlalchemy import func
from mako.lookup import TemplateLookup
import mako.exceptions
logger = logging.getLogger(__name__)

from ccvpn.models import DBSession, User, IcingaError, IcingaQuery, Gateway
from ccvpn.views import account, admin, api  # noqa


@view_config(route_name='home', renderer='home.mako')
def home(request):
    settings = request.registry.settings
    return {
        'eur_price': float(settings.get('paypal.month_price', 2)),
        'btc_price': float(settings.get('bitcoin.month_price', 0.02)),
        'motd': settings.get('motd'),
    }


@view_config(route_name='ca_crt')
def ca_crt(request):
    return HTTPOk(body=account.openvpn_ca)


page_lookup = None

@view_config(route_name='page', renderer='page.mako')
def page(request):
    global page_lookup
    if not page_lookup:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache = request.registry.settings.get('pages_cache')
        page_lookup = TemplateLookup(directories=[os.path.join(root, 'pages/')],
                                     module_directory=cache)

    try:
        template = page_lookup.get_template(request.matchdict['page'] + '.md')
        markdown_text = template.render(
            irc_username=request.user.username if request.user else '?',
        )
        md = markdown.Markdown(extensions=['toc', 'meta'])
        content = md.convert(markdown_text)
        title = md.Meta['title'][0] if 'title' in md.Meta else None
        return {'content': content, 'title': title}
    except mako.exceptions.TopLevelLookupException:
        return HTTPNotFound()


def format_bps(bits):
    multiples = ((1e9, 'G'), (1e6, 'M'), (1e3, 'K'), (0, ''))
    for d, m in multiples:
        if bits < d:
            continue
        n = bits / (d or 1)
        return '{:2g}{}bps'.format(n, m)


def get_uptime_factory(settings):
    base = settings.get('nagios.url')
    user = settings.get('nagios.user')
    password = settings.get('nagios.password')
    services = settings.get('nagios.service').split(',')
    services = [s.strip() for s in services]
    if base:
        try:
            r = IcingaQuery(base, (user, password))
        except IcingaError as e:
            logger.error('Icinga: %s', e.args[0])
            return lambda h: '[error]'

        def _get_uptime(host):
            try:
                uptimes = []
                for s in services:
                    uptimes.append(r.get_uptime(host, s))
                return sum(uptimes) / len(uptimes)
            except IcingaError as e:
                logger.error('Icinga: %s', e.args[0])
                return '[error]'

        return _get_uptime
    else:
        return lambda h: '[unknown]'


@view_config(route_name='status', renderer='status.mako')
def status(request):
    settings = request.registry.settings
    domain = settings.get('net_domain', '')
    gateways = DBSession.query(Gateway) \
                        .filter_by(enabled=True) \
                        .order_by(Gateway.country, Gateway.name) \
                        .all()
    l = list(gateways)

    get_uptime = get_uptime_factory(settings)

    for host in l:
        host.host_name = '%s-%s.%s'%(host.country, host.name, domain)
        host.uptime = get_uptime(host.host_name)
        host.bps_formatted = format_bps(host.bps)

    bw_graph_url = settings.get('munin.bw_graph_url', None)
    bw_graph_img = settings.get('munin.bw_graph_img', None)
    bw_graph = (bw_graph_url, bw_graph_img)
    return {
        'gateways': l,
        'bw_graph': bw_graph if all(bw_graph) else None,
        'n_users': DBSession.query(func.count(User.id))
                            .filter_by(is_paid=True).scalar(),
        'n_countries': len(set(i.country for i in l)),
        'total_bw': format_bps(sum(i.bps for i in l)),
    }


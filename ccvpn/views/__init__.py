import codecs
import markdown
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from ccvpn.views import account, admin, api

@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {
        'eur_price': float(request.registry.settings.get('paypal.month_price', 2)),
        'btc_price': float(request.registry.settings.get('bitcoin.month_price', 0.02))
    }


@view_config(route_name='page', renderer='page.mako')
def page(request):
    path = 'ccvpn/pages/'+request.matchdict['page']+'.md'
    try:
        f = codecs.open(path, mode="r", encoding="utf-8")
        content = markdown.markdown(f.read())
        return {'content': content}
    except FileNotFoundError:
        return HTTPNotFound()


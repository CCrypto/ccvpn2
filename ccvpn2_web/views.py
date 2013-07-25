from pyramid.response import Response
from pyramid.view import view_config
from .models import User, Order
from pyramid.httpexceptions import HTTPNotFound
import markdown
import os

@view_config(route_name='home', renderer='ccvpn2_web:templates/home.mako')
def home(request):
    return {}

@view_config(route_name='page', renderer='ccvpn2_web:templates/page.mako')
def page(request):
    path = 'ccvpn2_web/pages/'+request.matchdict['page']+'.md'
    try:
        f = open(path, 'r')
        content = markdown.markdown(f.read())
        return {'content':content}
    except FileNotFoundError:
        return HTTPNotFound()





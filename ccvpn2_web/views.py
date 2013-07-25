from pyramid.response import Response
from pyramid.view import view_config
from .models import User, Order

@view_config(route_name='home', renderer='ccvpn2_web:templates/home.mako')
def my_view(request):
    return {}








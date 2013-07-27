from pyramid.response import Response
from pyramid.view import view_config
from .models import DBSession, User, Order
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPSeeOther, HTTPBadRequest, HTTPNotFound
import markdown
import os

@view_config(route_name='home', renderer='ccvpn2_web:templates/home.mako')
def home(request):
    request.user
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

@view_config(route_name='account_login')
def a_login(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = DBSession.query(User).filter_by(username=username).first()
        assert user is not None
        assert user.check_password(password)
        request.session['uid'] = user.id
        request.session.flash(('info', 'Logged in.'))
        return HTTPSeeOther(location=request.route_url('home'))
    except KeyError:
        return HTTPBadRequest()
    except AssertionError:
        error = 'Invalid username/password.'
    request.session.flash(('error', error))
    return HTTPSeeOther(location=request.route_url('home'))



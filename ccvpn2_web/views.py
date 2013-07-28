from pyramid.response import Response
from pyramid.view import view_config
from .models import DBSession, User, Order
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from pyramid.httpexceptions import HTTPSeeOther, HTTPBadRequest, HTTPNotFound
import markdown
import os
import re
import transaction

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

@view_config(route_name='account_logout')
def a_logout(request):
    if 'uid' in request.session:
        del request.session['uid']
        request.session.flash(('info', 'Logged out.'))
    return HTTPSeeOther(location=request.route_url('home'))

@view_config(route_name='account_signup', renderer='ccvpn2_web:templates/signup.mako')
def a_signup(request):
    if request.method == 'POST':
        errors = []
        u = User()
        try:
            u.set_username(request.POST['username']) or \
                errors.append('Invalid username.')
            u.set_password(request.POST['password']) or \
                errors.append('Invalid password.')
            u.set_email(request.POST['email']) or \
                errors.append('Invalid email address.')
            if request.POST['password'] != request.POST['password2']:
                errors.append('Both passwords do not match.')
            assert not errors
            
            nc = DBSession.query(func.count(User.id).label('nc')).filter_by(username=u.username).subquery()
            ec = DBSession.query(func.count(User.id).label('ec')).filter_by(email=u.email).subquery()
            c  = DBSession.query(nc, ec).first()
            if c.nc > 0:
                errors.append('Username already registered.')
            if c.ec > 0:
                errors.append('E-mail address already registered.')
            assert not errors
            
            DBSession.add(u)
            transaction.commit() # Commit to have u.id
        except KeyError:
            return HTTPBadRequest()
        except AssertionError:
            for error in errors:
                request.session.flash(('error', error))
            return {k:request.POST[k] for k in ('username','password','password2','email')}
        request.session['uid'] = u.id
        return HTTPSeeOther(location=request.route_url('home'))
    return {}

@view_config(route_name='account_forgot', renderer='ccvpn2_web:templates/forgot_password.mako')
def a_forgot(request):
    if request.method == 'POST':
        try:
            u = DBSession.query(User) \
                .filter_by(username=request.POST['username']) \
                .first()
            if not u:
                raise Exception('Unknown username.')
            if not u.email:
                raise Exception('No e-mail address associated. Contact the support.')
            # TODO: Here, send a mail with a reset link
            request.session.flash(('info', 'We sent a reset link. Check your emails.'))
        except KeyError:
            return HTTPBadRequest()
        except Exception as e:
            request.session.flash(('error', e.args[0]))
    return {}

@view_config(route_name='account', renderer='ccvpn2_web:templates/account.mako')
def account(request):
    return {}


from pyramid.response import Response
from pyramid.view import view_config
from .models import DBSession, User, Order, GiftCode, APIAccessToken, Profile, random_profile_password
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from pyramid.httpexceptions import HTTPSeeOther, HTTPMovedPermanently, HTTPBadRequest, HTTPNotFound, HTTPUnauthorized
import markdown
import os
import re
import datetime
from pyramid.renderers import render_to_response
from . import methods

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
        return HTTPSeeOther(location=request.route_url('account'))
    except KeyError:
        return HTTPBadRequest()
    except AssertionError:
        error = 'Invalid username/password.'
    request.session.flash(('error', error))
    return HTTPSeeOther(location=request.route_url('home'))

@view_config(route_name='account_logout', permission='logged')
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
            u.validate_username(request.POST['username']) or \
                errors.append('Invalid username.')
            u.validate_password(request.POST['password']) or \
                errors.append('Invalid password.')
            u.validate_email(request.POST['email']) or \
                errors.append('Invalid email address.')
            if request.POST['password'] != request.POST['password2']:
                errors.append('Both passwords do not match.')
            assert not errors
            
            nc = DBSession.query(func.count(User.id).label('nc')).filter_by(username=request.POST['username']).subquery()
            ec = DBSession.query(func.count(User.id).label('ec')).filter_by(email=request.POST['email']).subquery()
            c  = DBSession.query(nc, ec).first()
            if c.nc > 0:
                errors.append('Username already registered.')
            if c.ec > 0:
                errors.append('E-mail address already registered.')
            assert not errors
            u.username = request.POST['username']
            u.email = request.POST['email']
            u.set_password(request.POST['password'])
            DBSession.add(u)
            DBSession.commit()
            request.session['uid'] = u.id
            return HTTPSeeOther(location=request.route_url('account'))
        except KeyError:
            return HTTPBadRequest()
        except AssertionError as e:
            for error in errors:
                request.session.flash(('error', error))
            return {k:request.POST[k] for k in ('username','password','password2','email')}
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


@view_config(route_name='account', request_method='POST', permission='logged', renderer='ccvpn2_web:templates/account.mako')
def account_post(request):
    # TODO: Fix that. split in two functions or something.
    errors = []
    try:
        if 'profilename' in request.POST:
            p = Profile()
            p.validate_name(request.POST['profilename']) or \
                errors.append('Invalid name.')
            assert not errors
            if DBSession.query(Profile).filter_by(uid=request.user.id, name=request.POST['profilename']).first():
                errors.append('Name already used.')
            assert not errors
            p.name = request.POST['profilename']
            p.askpw = 'askpw' in request.POST and request.POST['askpw'] == '1'
            p.uid = request.user.id
            if not p.askpw:
                p.password = random_profile_password()
            DBSession.add(p)
            DBSession.commit()
            return account(request)

        if 'profiledelete' in request.POST:
            p = DBSession.query(Profile) \
                .filter_by(id=int(request.POST['profiledelete'])) \
                .filter_by(uid=request.user.id) \
                .first()
            assert p or errors.append('Unknown profile.')
            DBSession.delete(p)
            DBSession.commit()
            return account(request)

        u = request.user
        if request.POST['password'] != '':
            u.validate_password(request.POST['password']) or \
                errors.append('Invalid password.')
            if request.POST['password'] != request.POST['password2']:
                errors.append('Both passwords do not match.')
        if request.POST['email'] != '':
            u.validate_email(request.POST['email']) or \
                errors.append('Invalid email address.')
        assert not errors

        if request.POST['email'] != '':
            c = DBSession.query(func.count(User.id).label('ec')).filter_by(email=request.POST['email']).first()
            if c.ec > 0:
                errors.append('E-mail address already registered.')
        assert not errors
        if request.POST['password'] != '':
            u.set_password(request.POST['password'])
        if request.POST['email'] != '':
            u.email = request.POST['email']
        DBSession.commit()
        request.session.flash(('info', 'Saved!'))

    except KeyError:
        return HTTPBadRequest()
    except AssertionError:
        for error in errors:
            request.session.flash(('error', error))
    return account(request)
    

@view_config(route_name='account', permission='logged', renderer='ccvpn2_web:templates/account.mako')
def account(request):
    return {'email':request.user.email}

@view_config(route_name='account_redirect')
def account_redirect(request):
    return HTTPMovedPermanently(location=request.route_url('account'))

@view_config(route_name='order_post', permission='logged')
def order_post(request):
    if 'code' in request.POST and request.POST['code'] != '':
        gc = DBSession.query(GiftCode) \
            .filter_by(code=request.POST['code'], used=None) \
            .first()
        if not gc:
            request.session.flash(('error', 'Unknown or already used code.'))
        else:
            request.user.add_paid_time(gc.time)
            gc.used = request.user.id
            added = gc.time.days
            request.session.flash(('info', 'OK! Added %d days to your account.'%added))
        DBSession.commit()
        return HTTPSeeOther(location=request.route_url('account'))
     
    times = (1, 3, 6, 12)
    try:
        
        assert request.POST['method'] in methods.METHODS
        assert int(request.POST['time']) in times
    except (KeyError, AssertionError):
        # there should not be any problems here
        return HTTPBadRequest()
    time = datetime.timedelta(days=30*int(request.POST['time']))
    o = Order(user=request.user, time=time)
    o.close_date = datetime.datetime.now()+datetime.timedelta(days=7)
    o.payment = {}
    method = methods.METHODS[request.POST['method']]()
    method.init(request, o)
    DBSession.add(o)
    DBSession.commit()
    return method.start(request, o)

@view_config(route_name='order_view', renderer='ccvpn2_web:templates/order.mako', permission='logged')
def order_view(request):
    id = int(request.matchdict['hexid'], 16)
    o = DBSession.query(Order).filter_by(id=id).first()
    if not o:
        return HTTPNotFound()
    if not request.user.is_admin and request.user.id != o.uid:
        return HTTPUnauthorized()
    return {'o':o}

@view_config(route_name='order_callback')
def order_callback(request):
    id = int(request.matchdict['hexid'], 16)
    o = DBSession.query(Order).filter_by(id=id).first()
    if not o:
        return HTTPNotFound()
    method = methods.METHOD_IDS[o.method]
    ret = method.callback(request, o)
    DBSession.commit()
    return ret

openvpn_remote = ('vpn-gw.ccrypto.org',)
ca_content = ""

@view_config(route_name='config', permission='logged')
def config(request):
    udp = request.matchdict['version'] == 'alpha'
    r = render_to_response('ccvpn2_web:templates/config.ovpn.mako',
        dict(username=request.user.username, udp=udp,
            remotes=openvpn_remote, ca_content=ca_content))
    r.content_type = 'test/plain'
    return r

@view_config(route_name='config_profile', permission='logged')
def config_profile(request):
    udp = request.matchdict['version'] == 'alpha'
    pname = request.matchdict['profile']
    profile = DBSession.query(Profile) \
        .filter_by(uid=request.user.id, name=pname) \
        .first()
    if not profile:
        return HTTPNotFound()
    r = render_to_response('ccvpn2_web:templates/config.ovpn.mako',
        dict(username=request.user.username, udp=udp, profile=profile,
            remotes=openvpn_remote, ca_content=ca_content))
    r.content_type = 'test/plain'
    return r


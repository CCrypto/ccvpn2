import datetime

import transaction
from sqlalchemy import func
from pyramid.view import view_config, forbidden_view_config
from pyramid.renderers import render, render_to_response
from pyramid.httpexceptions import (
    HTTPSeeOther, HTTPMovedPermanently,
    HTTPBadRequest, HTTPNotFound, HTTPForbidden, HTTPFound
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from ccvpn.models import (
    DBSession,
    User, Profile, PasswordResetToken, Gateway,
    random_access_token
)


# Set in __init__.py from app settings
openvpn_gateway = ''
openvpn_ca = ''


@forbidden_view_config()
def forbidden(request):
    _ = request.translate
    if not request.user:
        return HTTPFound(location=request.route_url('account_login'))
    return HTTPForbidden()


@view_config(route_name='account_login', renderer='login.mako')
def login(request):
    _ = request.translate
    if request.method != 'POST':
        return {}

    username = request.POST.get('username')
    password = request.POST.get('password')
    if not username or not password:
        request.response.status_code = HTTPBadRequest.code
        return {}

    user = DBSession.query(User).filter_by(username=username).first()
    if not user or not user.check_password(password):
        request.response.status_code = HTTPForbidden.code
        request.messages.error(_('Invalid username or password.'))
        return {}

    user.last_login = datetime.datetime.now()

    request.session['uid'] = user.id
    request.messages.info(_('Logged in.'))
    return HTTPSeeOther(location=request.route_url('account'))


@view_config(route_name='account_logout', permission='logged')
def logout(request):
    _ = request.translate
    if 'uid' in request.session:
        del request.session['uid']
        request.messages.info(_('Logged out.'))
    return HTTPSeeOther(location=request.route_url('home'))


@view_config(route_name='account_signup', renderer='signup.mako')
def signup(request):
    _ = request.translate
    if request.method != 'POST':
        return {}
    errors = []

    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        if not User.validate_username(username):
            errors.append(_('Invalid username.'))
        if not User.validate_password(password):
            errors.append(_('Invalid password.'))
        if email and not User.validate_email(email):
            errors.append(_('Invalid email address.'))
        if password != password2:
            errors.append(_('Both passwords do not match.'))

        assert not errors

        used = User.is_used(username, email)
        if used[0] > 0:
            errors.append(_('Username already registered.'))
        if used[1] > 0 and email:
            errors.append(_('E-mail address already registered.'))

        assert not errors

        with transaction.manager:
            u = User(username=username, email=email, password=password)
            if request.referrer:
                u.referrer_id = request.referrer.id
            DBSession.add(u)
            DBSession.flush()
            request.session['uid'] = u.id
        return HTTPSeeOther(location=request.route_url('account'))
    except AssertionError:
        for error in errors:
            request.messages.error(error)
        fields = ('username', 'password', 'password2', 'email')
        request.response.status_code = HTTPBadRequest.code
        return {k: request.POST[k] for k in fields}


@view_config(route_name='account_forgot', renderer='forgot_password.mako')
def forgot(request):
    _ = request.translate
    if request.method != 'POST' or 'username' not in request.POST:
        return {}

    u = DBSession.query(User) \
        .filter_by(username=request.POST['username']) \
        .first()
    if not u:
        request.messages.error(_('Unknown username.'))
        request.response.status_code = HTTPBadRequest.code
        return {}
    if not u.email:
        request.messages.error(_('No e-mail address associated with username.'))
        request.response.status_code = HTTPBadRequest.code
        return {}

    token = PasswordResetToken(u)
    DBSession.add(token)
    DBSession.flush()

    mailer = get_mailer(request)
    body = render('mail/password_reset.mako', {
        'user': u,
        'requested_by': request.remote_addr,
        'url': request.route_url('account_reset', token=token.token)
    })
    message = Message(subject=_('CCVPN: Password reset request'),
                      recipients=[u.email],
                      body=body)
    mailer.send(message)
    request.messages.info(_('We sent a reset link. Check your emails.'))
    return {}


@view_config(route_name='account_reset', renderer='reset_password.mako')
def reset(request):
    _ = request.translate
    token = DBSession.query(PasswordResetToken) \
        .filter_by(token=request.matchdict['token']) \
        .first()

    if not token or not token.user:
        request.messages.error(_('Unknown password reset token.'))
        url = request.route_url('account_forgot')
        return HTTPMovedPermanently(location=url)

    password = request.POST.get('password')
    password2 = request.POST.get('password2')

    if request.method != 'POST' or not password or not password2:
        return {'token': token}

    if not User.validate_password(password) or password != password2:
        request.messages.error(_('Invalid password.'))
        request.response.status_code = HTTPBadRequest.code
        return {'token': token}

    token.user.set_password(password)

    mailer = get_mailer(request)
    body = render('mail/password_reset_done.mako', {
        'user': token.user,
        'changed_by': request.remote_addr,
    })
    message = Message(subject=_('CCVPN: Password changed'),
                      recipients=[token.user.email],
                      body=body)
    mailer.send(message)

    msg = _('You have changed the password for ${user}.',
            mapping={'user': token.user.username})
    msg += ' ' + _('You can now log in.')
    request.messages.info(msg)
    DBSession.delete(token)
    url = request.route_url('account_login')
    return HTTPMovedPermanently(location=url)


@view_config(route_name='account', request_method='POST', permission='logged',
             renderer='account.mako')
def account_post(request):
    _ = request.translate
    # TODO: Fix that. split in two functions or something.
    errors = []
    try:
        if 'profilename' in request.POST:
            p = Profile()
            p.validate_name(request.POST['profilename']) or \
                errors.append(_('Invalid name.'))
            assert not errors
            name_used = DBSession.query(Profile) \
                .filter_by(uid=request.user.id,
                           name=request.POST['profilename']) \
                .first()
            if name_used:
                errors.append(_('Name already used.'))
            profiles_count = DBSession.query(func.count(Profile.id)) \
                .filter_by(uid=request.user.id).scalar()
            if profiles_count > 10:
                errors.append(_('You have too many profiles.'))
            assert not errors
            p.name = request.POST['profilename']
            p.askpw = 'askpw' in request.POST and request.POST['askpw'] == '1'
            p.uid = request.user.id
            if not p.askpw:
                p.password = random_access_token()
            DBSession.add(p)
            DBSession.flush()
            return account(request)

        if 'profiledelete' in request.POST:
            p = DBSession.query(Profile) \
                .filter_by(id=int(request.POST['profiledelete'])) \
                .filter_by(uid=request.user.id) \
                .first()
            assert p or errors.append(_('Unknown profile.'))
            DBSession.delete(p)
            DBSession.flush()
            return account(request)

        u = request.user
        if request.POST['password'] != '':
            u.validate_password(request.POST['password']) or \
                errors.append(_('Invalid password.'))
            if request.POST['password'] != request.POST['password2']:
                errors.append(_('Both passwords do not match.'))
        if request.POST['email'] != '':
            u.validate_email(request.POST['email']) or \
                errors.append(_('Invalid email address.'))
        assert not errors

        new_email = request.POST.get('email')
        if new_email and new_email != request.user.email:
            c = DBSession.query(func.count(User.id).label('ec')) \
                .filter_by(email=new_email).first()
            if c.ec > 0:
                errors.append(_('E-mail address already registered.'))
        assert not errors
        if request.POST['password'] != '':
            u.set_password(request.POST['password'])
        if request.POST['email'] != '':
            u.email = request.POST['email']
        request.messages.info(_('Saved!'))
        DBSession.flush()

    except KeyError:
        return HTTPBadRequest()
    except AssertionError:
        for error in errors:
            request.session.flash(('error', error))
    return account(request)


@view_config(route_name='account', permission='logged',
             renderer='account.mako')
def account(request):
    _ = request.translate
    return {
        'gw_countries': set(i[0] for i in DBSession.query(Gateway.country).all()),
    }


@view_config(route_name='account_redirect')
def account_redirect(request):
    _ = request.translate
    return HTTPMovedPermanently(location=request.route_url('account'))


@view_config(route_name='config', permission='logged')
def config(request):
    _ = request.translate
    settings = request.registry.settings
    domain = settings.get('net_domain', '')

    gw_countries = [i[0] for i in DBSession.query(Gateway.country).all()]

    pname = request.GET.get('profile')
    if pname:
        profile = DBSession.query(Profile) \
            .filter_by(uid=request.user.id, name=pname) \
            .first()
        if not profile:
            return HTTPNotFound()
    else:
        profile = None

    gw = request.GET.get('gw')
    if gw and gw[0:3] == 'rr_' and gw[3:] in gw_countries:
        gateway = 'gw.' + gw[3:] + '.' + domain
    else:
        gateway = 'gw.random.' + domain

    os = request.GET.get('os')

    # These clients do not fully support OpenVPN config
    not_real_ovpn = os == 'android' or os == 'ios'

    params = {
        'force_tcp': not_real_ovpn or 'forcetcp' in request.GET,
        'windows_dns': os == 'windows',
        'resolvconf': os == 'ubuntu',
        'username': request.user.username,
        'profile': profile,
        'gateway': gateway,
        'openvpn_ca': openvpn_ca,
    }

    r = render_to_response('config.ovpn.mako', params, request=request)
    r.content_type = 'application/octet-stream'
    return r


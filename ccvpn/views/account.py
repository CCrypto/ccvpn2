import datetime
from urllib.parse import urlencode

import transaction
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
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
    User, Profile, PasswordResetToken, Gateway, VPNSession, Order,
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
    if not user or not user.is_active or not user.check_password(password):
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
    }, request=request)
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
    }, request=request)
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

    try:
        username = request.matchdict['username']
        pname = request.matchdict['pname']

        if request.user.username != username:
            # Only allow corrently logged user for now
            raise ValueError()
        user = request.user

        profile = DBSession.query(Profile) \
                           .filter_by(uid=user.id) \
                           .filter_by(name=pname) \
                           .one()
    except (KeyError, NoResultFound):
        return HTTPNotFound()

    if profile.gateway_id:
        gateway = 'gw.%s-%s' % (profile.gateway.country, profile.gateway.name)
    elif profile.gateway_country:
        gateway = 'gw.%s' % (profile.gateway_country)
    else:
        gateway = 'gw.random'

    if not domain.startswith('.'):
        gateway += '.'
    gateway += domain


    os = profile.client_os

    # These clients do not fully support OpenVPN config
    # => force TCP, because we cannot try UDP first.
    os_require_tcp = os == 'android' or os == 'ios'
    force_tcp = profile.force_tcp or os_require_tcp

    params = {
        'force_tcp': force_tcp,
        'windows_dns': os == 'windows',
        'resolvconf': os == 'ubuntu',
        'ipv6': not profile.disable_ipv6,
        'dhcp': os != 'freebox',
        'http_proxy': profile.use_http_proxy,
        'username': request.user.username,
        'profile': profile,
        'gateway': gateway,
        'openvpn_ca': openvpn_ca,
    }

    r = render_to_response('config.ovpn.mako', params, request=request)
    r.content_type = 'application/x-openvpn-profile'
    return r


@view_config(route_name='account', permission='logged',
             renderer='account/index.mako')
def account(request):
    _ = request.translate

    ref_url = 'https://vpn.ccrypto.org/?ref=' + str(request.user.id)


    twitter_url = 'https://twitter.com/intent/tweet?'
    twitter_args = {
        'text': _('Awesome VPN! 2€/0.005BTC per month, with a free 7 days trial!'),
        'via': 'CCrypto_VPN',
        'url': ref_url,
        'related': 'CCrypto_VPN,CCrypto_org'
    }

    profiles_limit = 10
    return {
        'ref_url': ref_url,
        'twitter_link': twitter_url + urlencode(twitter_args),
        'profiles': request.user.profiles,
        'limit': profiles_limit,
    }
    return {}


@view_config(route_name='account', permission='logged',
             request_method='POST')
def account_post(request):
    _ = request.translate
    redirect = HTTPSeeOther(location=request.route_url('account'))
    profiles_limit = 10

    profile_name = request.POST.get('profilename')
    profile_delete = request.POST.get('delete')

    if profile_name:
        p = Profile()
        if not p.validate_name(profile_name):
            request.messages.error(_('Invalid name.'))
            return redirect

        # Check if the name is already used
        used = DBSession.query(Profile).filter_by(uid=request.user.id) \
                        .filter_by(name=profile_name).first()
        if used:
            request.messages.error(_('Name already used.'))
            return redirect

        # Check if this user's under the profile number limit
        profiles_count = DBSession.query(func.count(Profile.id)) \
                                  .filter_by(uid=request.user.id).scalar()
        if profiles_count > profiles_limit:
            request.messages.error(_('You have too many profiles.'))
            return redirect

        p.name = profile_name
        p.uid = request.user.id
        DBSession.add(p)
        DBSession.flush()
        return HTTPSeeOther(location=request.route_url('account_profiles_edit', id=p.id))

    if profile_delete:
        try:
            profile_delete = int(profile_delete)
        except ValueError:
            return redirect

        p = DBSession.query(Profile) \
            .filter_by(id=int(profile_delete)) \
            .filter_by(uid=request.user.id) \
            .first()

        if not p:
            request.messages.error(_('Unknown profile.'))
            return redirect

        DBSession.delete(p)

    return redirect


@view_config(route_name='account_profiles_edit', permission='logged',
             renderer='account/profiles_edit.mako')
def profiles_edit(request):
    _ = request.translate
    try:
        profile_id = int(request.matchdict['id'])
        profile = DBSession.query(Profile).filter_by(id=profile_id) \
                           .filter_by(uid=request.user.id).one()
    except (KeyError, ValueError, NoResultFound):
        return HTTPSeeOther(location=request.route_url('account'))

    return {
        'profile': profile,
        'edit_post_url': request.route_url('account_profiles_edit', id=profile.id),
        'gw_countries': set(i[0] for i in DBSession.query(Gateway.country).all()),
        'oses': {
            'windows': 'Windows',
            'android': 'Android',
            'ubuntu': 'Ubuntu',
            'osx': 'OS X',
            'freebox': 'Freebox',
            'other': _('Other / GNU/Linux'),
        },
    }

@view_config(route_name='account_profiles_edit', permission='logged',
             request_method='POST')
def profiles_edit_post(request):
    _ = request.translate
    try:
        profile_id = int(request.matchdict['id'])
        profile = DBSession.query(Profile).filter_by(id=profile_id) \
                           .filter_by(uid=request.user.id).one()
    except (KeyError, ValueError, NoResultFound):
        return HTTPSeeOther(location=request.route_url('account'))

    redirect = HTTPSeeOther(location=request.route_url('account_profiles_edit',
                                                       id=profile.id))

    try:
        name = request.POST['name']
        client_os = request.POST['client_os']
        gateway = request.POST['gateway']
        force_tcp = 'force_tcp' in request.POST
        disable_ipv6 = 'enable_ipv6' not in request.POST
        http_proxy = request.POST.get('use_http_proxy', '')
    except (KeyError, ValueError):
        return redirect


    if name != profile.name:
        if not p.validate_name(profile_name):
            request.messages.error(_('Invalid name.'))
            return redirect

        # Check if the name is already used
        used = DBSession.query(Profile).filter_by(uid=request.user.id) \
                        .filter_by(name=profile_name).first()
        if used:
            request.messages.error(_('Name already used.'))
            return redirect

    profile.name = name
    profile.client_os = client_os
    profile.force_tcp = force_tcp
    profile.disable_ipv6 = disable_ipv6
    profile.use_http_proxy = http_proxy

    if gateway.startswith('rr_') and len(gateway) == 5:
        # rr_<cc>  # random in country
        cc = gateway[3:]
        profile.gateway_country = cc
        profile.gateway_id = None
    else:
        # random
        profile.gateway_country = None
        profile.gateway_id = None

    request.messages.info(_('Saved!'))
    return HTTPSeeOther(location=request.route_url('account'))

@view_config(route_name='account_settings', permission='logged',
             renderer='account/settings.mako')
def settings(request):
    return {}


@view_config(route_name='account_settings', permission='logged',
             request_method='POST')
def settings_post(request):
    _ = request.translate

    try:
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']
    except:
        return HTTPSeeOther(location=request.route_url('account_settings'))

    if password and not request.user.validate_password(password):
        request.messages.error(_('Invalid password.'))
        password = ''
    if password and password != password2:
        request.messages.error(_('Both passwords do not match.'))
        password = ''

    if email and not request.user.validate_email(request.POST['email']):
        request.messages.error(_('Invalid email address.'))
        email = ''

    if email:
        # we do not count the current user (because of pre-filled forms)
        c = DBSession.query(func.count(User.id)).filter_by(email=email) \
                     .filter(User.id != request.user.id).scalar()
        if c > 0:
            request.messages.error(_('E-mail address already registered.'))
            email = ''

    if password:
        request.user.set_password(password)
    if email:
        request.user.email = email
    if password or email:
        request.messages.info(_('Saved!'))

    return HTTPSeeOther(location=request.route_url('account_settings'))


@view_config(route_name='account_orders', permission='logged',
             renderer='account/orders.mako')
def orders(request):
    items_count = DBSession.query(func.count(Order.id)) \
                           .filter_by(uid=request.user.id) \
                           .filter(Order.close_date != None) \
                           .scalar()
    page_items = 100
    pages = int((items_count / page_items) + 0.5)
    try:
        page = int(request.GET['page'])
    except (KeyError, ValueError):
        page = 0
    offset = page * page_items
    orders = DBSession.query(Order).filter_by(uid=request.user.id) \
                    .filter(Order.close_date != None) \
                    .order_by(Order.start_date.desc()) \
                    .limit(page_items).offset(offset)
    return {'orders': orders, 'page': page, 'pages': pages}



@view_config(route_name='account_logs', permission='logged',
             renderer='account/logs.mako')
def logs(request):
    items_count = DBSession.query(func.count(VPNSession.id)) \
                           .filter_by(user_id=request.user.id) \
                           .scalar()
    page_items = 100
    pages = int((items_count / page_items) + 0.5)
    try:
        page = int(request.GET['page'])
    except (KeyError, ValueError):
        page = 0
    offset = page * page_items
    logs = DBSession.query(VPNSession).filter_by(user_id=request.user.id) \
                    .order_by(VPNSession.connect_date.desc()) \
                    .limit(page_items).offset(offset)
    return {'logs': logs, 'page': page, 'pages': pages}



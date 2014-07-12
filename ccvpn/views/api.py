import json
import datetime

import transaction
from pyramid.view import view_config
from ccvpn.models import DBSession, User, Gateway, Profile, VPNSession
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPForbidden
)

gw_versions = {
    'alpha': 1,
    'beta': 2,
    'socks': 3,
}

def require_api_token(function=None):
    def _dec(view_func):
        def _func(request):
            if not 'X-Gateway-Token' in request.headers:
                return HTTPBadRequest('require X-Gateway-Token header.')
            if not 'X-Gateway-Version' in request.headers:
                return HTTPBadRequest('require X-Gateway-Version header.')
            if request.headers['X-Gateway-Version'] not in gw_versions:
                return HTTPBadRequest('invalid X-Gateway-Version.')
            version = gw_versions[request.headers['X-Gateway-Version']]

            token = request.headers['X-Gateway-Token']
            gw = DBSession.query(Gateway) \
                .filter_by(token=token).first()
            if not gw:
                return HTTPForbidden('Unknown token.')
            if not gw.enabled:
                return HTTPForbidden('Gateway disabled.')

            ra = request.remote_addr
            if gw.ipv4 == ra or gw.ipv6 == ra or gw.ipv6 == '::ffff:'+ra:
                request.gw = gw
                request.gw_version = version
                return view_func(request)
            return HTTPForbidden('Source address not authorized for this'
                                    'gateway.')
        return _func
    if function is None:
        return _dec
    else:
        return _dec(function)


@view_config(route_name='api_gateway_auth', request_method='POST')
@require_api_token
def api_gateway_auth(request):
    try:
        fullname = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return HTTPBadRequest('Require username/password')

    if '/' in fullname:
        username, profilename = fullname.split('/', 1)
    else:
        username = fullname
        profilename = None

    user = DBSession.query(User).filter_by(username=username).first()
    if not user or not user.check_password(password) or not user.is_active:
        return HTTPForbidden('Invalid username or password.')
    if not user.is_paid:
        return HTTPForbidden('Free account')

    if profilename:
        profile = DBSession.query(Profile) \
                           .filter_by(name=profilename, uid=user.id).first()
        if not profile:
            return HTTPForbidden('Unknown profile')
    return HTTPOk(empty_body=True)


@view_config(route_name='api_gateway_disconnect', request_method='POST')
@require_api_token
def api_gateway_disconnect(request):
    try:
        fullname = request.POST['username']
        bytes_up = request.POST['bytes_up']
        bytes_down = request.POST['bytes_down']
    except KeyError:
        return HTTPBadRequest('Require username/bytes_up/bytes_down')

    if '/' in fullname:
        username, profilename = fullname.split('/', 1)
    else:
        username = fullname
        profilename = None

    sesq = DBSession.query(VPNSession) \
                    .filter(VPNSession.disconnect_date == None) \
                    .filter(VPNSession.gateway_id == request.gw.id) \
                    .filter(VPNSession.gateway_version == request.gw_version) \
                    .filter(User.username == username) \
                    .join(User)
    if profilename:
        sesq = sesq.filter(Profile.uid == User.id) \
                   .filter(Profile.name == profilename) \
                   .join(Profile)
    sessions = list(sesq.all())

    # First, we close every sessions except the last
    # This can happen in /disconnect is not called
    for sess in sessions[:-1]:
        sess.disconnect_date = datetime.datetime.now()
        sess.bytes_up = 0
        sess.bytes_down = 0

    # Now we can close the right session and save bw stats
    if sessions:
        sess = sessions[-1]
        sess.disconnect_date = datetime.datetime.now()
        sess.bytes_up = bytes_up
        sess.bytes_down = bytes_down
    return HTTPOk(empty_body=True)


@view_config(route_name='api_gateway_connect', request_method='POST')
@require_api_token
def api_gateway_connect(request):
    try:
        fullname = request.POST['username']
        client_addr = request.POST['remote_addr']
    except KeyError:
        return HTTPBadRequest('Require username/remote_addr')

    if '/' in fullname:
        username, profilename = fullname.split('/', 1)
    else:
        username = fullname
        profilename = None

    user = DBSession.query(User).filter_by(username=username).first()
    if not user or not user.is_active or not user.is_paid:
        return HTTPForbidden('Invalid account')

    sess = VPNSession()
    sess.gateway_id = request.gw.id
    sess.gateway_version = request.gw_version
    sess.user_id = user.id
    sess.remote_addr = client_addr

    if profilename:
        profile = DBSession.query(Profile) \
                           .filter_by(name=profilename, uid=user.id).first()
        if not profile:
            return HTTPForbidden('Unknown profile')
        sess.profile_id = profile.id

    DBSession.add(sess)

    params = {}

    return HTTPOk(body=json.dumps(params))


@view_config(route_name='api_public_gateways', request_method='GET')
def api_public_gateways(request):
    domain = request.registry.settings.get('net_domain', '')
    q = DBSession.query(Gateway)

    show_disabled = request.GET.get('show_disabled')

    country = request.GET.get('country')
    hostname = request.GET.get('hostname')

    if country:
        q = q.filter(Gateway.country == country)

    if hostname:
        if '-' in hostname:
            hn_country, hn_name = hostname.split('-', 1)
            q = q.filter(Gateway.country == hn_country)
            q = q.filter(Gateway.name == hn_name)
        elif country:
            q = q.filter(Gateway.name == hostname)
        else:
            return HTTPOk(body=json.dumps([]), content_type="application/json")
            

    if not show_disabled:
        q = q.filter(Gateway.enabled == True)

    def out(g):
        return {
            'hostname': g.country + '-' + g.name,
            'fqdn': g.country + '-' + g.name + '.' + domain,
            'country': g.country,
            'bandwidth': g.bps,
            'ipv4': g.ipv4,
            'ipv6': g.ipv6,
            'enabled': g.enabled,
        }

    r = [out(g) for g in q.all()]
    return HTTPOk(body=json.dumps(r), content_type="application/json")


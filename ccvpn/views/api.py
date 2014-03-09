from pyramid.view import view_config
from ccvpn.models import DBSession, User, APIAccessToken, Profile
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPUnauthorized
)


def require_api_token(function=None):
    def _dec(view_func):
        def _func(request):
            if not 'X-API-Token' in request.headers:
                return HTTPBadRequest('require API token header.')
            token = request.headers['X-API-Token']
            at = DBSession.query(APIAccessToken) \
                .filter_by(token=token).first()
            if not at:
                return HTTPForbidden('wrong API token')
            if at.remote_addr and at.remote_addr != request.remote_addr \
               and at.remote_addr != '::ffff:' + request.remote_addr:
                return HTTPUnauthorized('remote address not allowed for this'
                                        'token')
            return view_func(request)
        return _func
    if function is None:
        return _dec
    else:
        return _dec(function)


@view_config(route_name='api_server_auth', request_method='POST')
@require_api_token
def api_server_auth(request):
    if 'username' not in request.POST or 'password' not in request.POST:
        return HTTPBadRequest()
    fullname = request.POST['username']
    password = request.POST['password']
    if '/' in fullname:
        username, profilename = fullname.split('/', 1)
    else:
        username = fullname
        profilename = None
    user = DBSession.query(User).filter_by(username=username).first()
    if not user or not user.check_password(password) or not user.is_active:
        return HTTPForbidden()
    if not user.is_paid:
        return HTTPUnauthorized()
    if profilename:
        profile = DBSession.query(Profile) \
            .filter_by(name=profilename, uid=user.id).first()
        if not profile:
            return HTTPForbidden()
    return HTTPOk()


@view_config(route_name='api_server_disconnect', request_method='POST')
@require_api_token
def api_server_disconnect(request):
    # May be used to count login/logouts
    # Empty for now
    return HTTPOk(empty_body=True)


@view_config(route_name='api_server_config', request_method='GET')
@require_api_token
def api_server_config(request):
    if 'username' not in request.GET:
        return HTTPBadRequest()
    fullname = request.GET['username']
    if '/' in fullname:
        username, profilename = fullname.split('/', 1)
    else:
        username = fullname
        profilename = None
    user = DBSession.query(User).filter_by(username=username).first()
    if not user:
        return HTTPNotFound('unknown user')
    if profilename:
        profile = DBSession.query(Profile) \
            .filter_by(name=profilename, uid=user.id) \
            .first()
        if not profile:
            return HTTPNotFound('unknown profile')
    # Nothing here, we do not need per-client configuration
    # Mostly for future uses (BW limit, user routes, port forwarding, ...)
    return HTTPOk(empty_body=True)


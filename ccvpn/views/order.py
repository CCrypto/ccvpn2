import datetime

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPSeeOther,
    HTTPBadRequest, HTTPNotFound, HTTPUnauthorized
)
from ccvpn.models import (
    DBSession,
    GiftCode, AlreadyUsedGiftCode,
    Order,
)


def order_post_gc(request, code):
    try:
        gc = GiftCode.one(code=code)
        gc.use(request.user)

        time = gc.time.days
        request.messages.info(_('OK! Added ${time} days to your account.',
                                mapping={'time': time}))
        DBSession.flush()
    except (NoResultFound, MultipleResultsFound):
        request.messages.error(_('Unknown gift code.'))
    except AlreadyUsedGiftCode:
        request.messages.error(_('Gift code already used.'))
    return HTTPSeeOther(location=request.route_url('account'))


@view_config(route_name='order_post', permission='logged')
def order_post(request):
    _ = request.translate
    code = request.POST.get('code')
    if code:
        return order_post_gc(request, code)

    times = (1, 3, 6, 12)
    try:
        method_name = request.POST.get('method')
        time_months = int(request.POST.get('time'))
    except (ValueError, TypeError):
        return HTTPSeeOther(location=request.route_url('account'))

    if method_name == 'admin' and request.user.is_admin:
        time = datetime.timedelta(days=30 * time_months)
        request.user.add_paid_time(time)
        return HTTPSeeOther(location=request.route_url('account'))

    method = request.payment_methods.get(method_name)
    if not method or time_months not in times:
        return HTTPBadRequest('Invalid method/time')

    time = datetime.timedelta(days=30 * time_months)

    o = method.init(request.user, time)
    DBSession.add(o)
    DBSession.flush()
    return method.start(request, o)


@view_config(route_name='order_view', renderer='order.mako',
             permission='logged')
def order_view(request):
    _ = request.translate
    id = int(request.matchdict['hexid'], 16)
    o = DBSession.query(Order).filter_by(id=id).first()
    if not o:
        return HTTPNotFound()
    if not request.user.is_admin and request.user.id != o.uid:
        return HTTPUnauthorized()
    method = request.payment_methods.get(o.method)
    r = {'o': o}
    try:
        r.update(method.view(request, o))
    except NotImplementedError:
        pass
    return r


@view_config(route_name='order_callback')
def order_callback(request):
    _ = request.translate
    id = int(request.matchdict['hexid'], 16)
    o = DBSession.query(Order).filter_by(id=id).first()
    if not o:
        return HTTPNotFound()

    method = request.payment_methods.get(o.method)
    r = method.callback(request, o)
    DBSession.flush()
    return r



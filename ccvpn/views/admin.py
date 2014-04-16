import copy
from datetime import datetime, timedelta, date

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPException,
    HTTPSeeOther,
    HTTPBadRequest, HTTPNotFound, HTTPMethodNotAllowed,
)
from pyramid.renderers import render_to_response
from dateutil import parser

from ccvpn.models import (
    DBSession,
    User, Order, VPNSession, Profile,
    GiftCode, Gateway,
)
from ccvpn import methods


def monthdelta(date, delta):
    m = (date.month + delta) % 12
    y = date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0
                       else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
                       ][m - 1])
    return date.replace(day=d, month=m, year=y)


def last_days(n=30):
    now = date.today()
    for i in range(n - 1, -1, -1):
        yield now - timedelta(days=i)


def last_months(n=12):
    now = date.today().replace(day=1)
    for i in range(n - 1, -1, -1):
        yield monthdelta(now, -i)


def time_filter(period, m, df):
    def _filter(o):
        if period == 'm':
            return df(o).date() == m
        if period == 'y':
            return df(o).date().replace(day=1) == m
    return _filter


def time_filter_future(period, m, df):
    def _filter(o):
        if period == 'm':
            return df(o).date() <= m
        if period == 'y':
            return df(o).date().replace(day=1) <= m
    return _filter


@view_config(route_name='admin_graph', permission='admin')
def admin_graph(request):
    graph_name = request.matchdict['name']

    try:
        import pygal
    except ImportError:
        raise HTTPNotFound()

    def get(name, default=None, type=str):
        try:
            return type(request.GET.get(name, default))
        except ValueError:
            raise HTTPBadRequest()

    pygalopts = {
        'js': [
            request.static_url('ccvpn:static/pygal/svg.jquery.js'),
            request.static_url('ccvpn:static/pygal/pygal-tooltips.js')
        ]
    }

    period = get('period', 'm')
    if period == 'm':
        period_time = timedelta(days=30)
    if period == 'y':
        period_time = timedelta(days=365)

    if graph_name == 'users':
        period = get('period', 'm')

        chart = pygal.Line(fill=True, x_label_rotation=75, show_legend=False,
                           **pygalopts)
        chart.title = 'Users (%s)' % period
        chart.x_labels = []
        values = []
        gen = last_days(30) if period == 'm' else last_months(12)
        users = DBSession.query(User).all()

        for m in gen:
            filter_ = time_filter_future(period, m, lambda o: o.signup_date)
            users_filtered = filter(filter_, users)
            values.append(len(list(users_filtered)))
            chart.x_labels.append('%s/%s/%s' % (m.year, m.month, m.day))

        chart.add('Users', values)
        return Response(chart.render(), content_type='image/svg+xml')

    elif graph_name == 'income':
        method = get('method', 0, int)
        if not method in request.payment_methods:
            raise HTTPNotFound()
        method_name = request.payment_methods[method].name

        chart = pygal.StackedBar(x_label_rotation=75, show_legend=True,
                                 **pygalopts)
        chart.title = 'Income (%s, %s)' % (method_name, period)
        orders = DBSession.query(Order) \
            .filter(Order.start_date > datetime.now() - period_time) \
            .filter(Order.method == method) \
            .filter(Order.paid == True) \
            .all()

        # Prepare value dict
        values = {}
        for order in orders:
            t = order.time
            if t not in values:
                values[t] = []

        chart.x_labels = []
        gen = last_days(30) if period == 'm' else last_months(12)
        for m in gen:
            filter_ = time_filter(period, m, lambda o: o.start_date)
            orders_date = list(filter(filter_, orders))

            for duration in values.keys():
                filter_ = lambda o: o.time == duration
                orders_dd = list(filter(filter_, orders_date))

                sum_ = sum(o.paid_amount for o in orders_dd)
                values[duration].append(round(sum_, 4) or None)

            chart.x_labels.append('%s' % m)

        for time, v in values.items():
            label = '%sd' % time.days
            chart.add(label, v)
        return Response(chart.render(), content_type='image/svg+xml')
    else:
        raise HTTPNotFound()


class AdminBase(object):
    def __init__(self, parent):
        self.parent = parent
        self.templates = []
        self.main_template = None
        self.id = None

    @property
    def left_menu(self):
        """ Generate the side menu.
            It is meant to be overridden to change the menu.
        """
        if self.parent:
            return self.parent.left_menu
        return []

    def context_rev(self):
        """ Returns reversed context as a list of AdminBase objects """
        c = self
        l = []
        while c:
            l = [c] + l
            c = c.parent
        return l

    def without_id(self):
        """ Copy self without id """
        o = copy.copy(self)
        o.id = None
        return o

    def __resource_url__(self, request, info):
        url = ''
        c = self
        while c:
            part = ''
            if c.__name__:
                part += '/' + c.__name__
            if c.id:
                part += '/' + str(c.id)
            url = part + url
            c = c.parent
        return request.route_url('admin_traversal', traverse=url[1:])

    def __getitem__(self, name):
        if self.subobjects:
            return self.subobjects[name](self)

    @property
    def __name__(self):
        return self.name

    def post(self, request):
        raise NotImplementedError()

    def get(self, request):
        raise NotImplementedError()


class AdminBaseModel(AdminBase):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.name = self.model.__name__.lower() + 's'

        def filter(q):
            if self.id:
                return q.filter(self.model.id == self.id)
            return q

        self.get_item_filters = [filter]
        self.get_list_filters = [filter]

        p = parent
        while p:
            if not isinstance(p, AdminBaseModel):
                # Skip AdminBase instances
                break
            self.get_item_filters += p.get_item_filters
            self.get_list_filters += p.get_list_filters
            p = p.parent

        self.list_fields = []
        self.edit_fields = []

    @property
    def title(self):
        if self.id:
            return '#%d [ %s ]' % (self.id, str(self.item))
        elif hasattr(self, '_title'):
            return self._title
        else:
            return self.name

    @title.setter
    def title(self, value):
        self._title = value

    def post(self, request):
        if self.id:
            query = DBSession.query(self.model).filter_by(id=self.id)
            parent = self.parent
            while parent:
                if not isinstance(parent, AdminBaseModel):
                    break
                query = query.filter(parent.model.id == parent.id)
                parent = parent.parent
            self.item = query.first() or self.model()
        else:
            self.item = self.model()

        for field in self.edit_fields:
            if not field.writable:
                continue
            in_value = request.POST.get(field.id)
            if in_value:
                value = field.ifilter(in_value)
                value = value or None
            else:
                value = None
            setattr(self.item, field.attr, value)

        DBSession.add(self.item)
        DBSession.flush()

        request.messages.info('Saved!')

        location = request.resource_url(self)
        DBSession.expire_all()
        return HTTPSeeOther(location=location)

    def get(self, request):
        if self.id:
            return self.get_item(self.id)
        else:
            return self.get_list()

    def get_item(self, id):
        query = DBSession.query(self.model).filter_by(id=id)
        for f in self.get_item_filters:
            query = f(query)
        self.item = query.first()
        self.main_template = 'item.mako'
        if self.item is None:
            raise HTTPNotFound()
        return {'item': self.item}

    def get_list(self):
        query = DBSession.query(self.model).order_by(self.model.id)
        for f in self.get_list_filters:
            query = f(query)
        items = query.all()
        self.main_template = 'list.mako'
        return {'list_items': items}

    def __getitem__(self, name):
        if self.id:
            if self.subobjects:
                return self.subobjects[name](self)
        else:
            try:
                self.id = int(name)
                self.get_item(self.id)
                # FIXME: split get_item()
            except ValueError:
                raise HTTPNotFound('Invalid id')
            return self


class ListField(object):
    def __init__(self, name, attr, link=None, filter=None):
        self.name = name
        self.attr = attr or name
        self.link = link
        self.filter = filter or (lambda v: v)


class ListFieldID(ListField):
    def __init__(self, name='ID', attr='id', link=None):
        def id_filter(v):
            return '#' + str(v)
        super().__init__(name=name, attr=attr, link=link, filter=id_filter)


class EditField(object):
    def __init__(self, name, attr=None, **kwargs):
        self.name = name
        self.attr = attr or name
        self.ifilter = kwargs.get('ifilter', (lambda v: v))
        self.ofilter = kwargs.get('ofilter', (lambda v: v))
        self.writable = kwargs.get('writable', True)

    @property
    def id(self):
        """ Unique ID for the Field. """
        return self.attr


class EditFieldID(EditField):
    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'ID')
        kwargs.setdefault('attr', 'id')
        kwargs.setdefault('writable', False)
        super().__init__(**kwargs)


class AdminRoot(AdminBase):
    def __init__(self):
        super().__init__(None)
        self.subobjects = {
            'users': AdminUser,
            'gateways': AdminGateway,
            'giftcodes': AdminGiftCode,

            'stats': AdminStats,
        }
        self.name = ''
        self.title = 'Admin'

    @property
    def left_menu(self):
        return (
            ('/admin/users', 'Users'),
            ('/admin/giftcodes', 'Gift Codes'),
            ('/admin/gateways', 'Gateways'),
            None,
            ('/admin/stats', 'Stats'),
        )

    def get(self, request):
        self.main_template = 'home.mako'
        return {}

    def post(self, request):
        return self.get(request)


class AdminUser(AdminBaseModel):
    def __init__(self, parent):
        super().__init__(parent, User)

        self.subobjects = {
            'vpnsessions': AdminSession,
            'orders': AdminOrder,
            'profiles': AdminProfile,
        }
        self.title = 'Users'

        def list_f(q):
            return q.order_by(self.model.id.desc()) \
                    .limit(20)
        self.get_list_filters.append(list_f)

        self.list_fields = (
            ListFieldID(link='/admin/users/{id}'),
            ListField('Username', 'username'),
            ListField('E-Mail', 'email'),
            ListField('Active?', 'is_active'),
            ListField('Admin?', 'is_admin'),
        )
        self.edit_fields = (
            EditFieldID(),
            EditField('Username', 'username'),
        )

    @property
    def left_menu(self):
        if self.id:
            return (
                ('/admin/users/%s/vpnsessions' % self.id, 'VPNSessions'),
                ('/admin/users/%s/orders' % self.id, 'Orders'),
                ('/admin/users/%s/profiles' % self.id, 'Profiles'),
            )
        else:
            return super().left_menu

    def get_list(self):
        r = super().get_list()
        r['list_title'] = 'New users'
        return r

    def get_item(self, id):
        r = super().get_item(id)
        return r


class AdminSession(AdminBaseModel):
    def __init__(self, au):
        super().__init__(parent=au, model=VPNSession)
        self.title = 'VPN Sessions'

        self.list_fields = (
            ListFieldID(link='/admin/users/{user_id}/vpnsessions/{id}'),
            ListField('Gateway', 'gateway', link='/admin/gateways/{gateway_id}'),
            ListField('Connect', 'connect_date'),
            ListField('Disconnect', 'disconnect_date'),
            ListField('Remote Address', 'remote_addr'),
        )
        self.edit_fields = (
            EditFieldID(),
        )


class AdminOrder(AdminBaseModel):
    def __init__(self, au):
        super().__init__(parent=au, model=Order)
        self.title = 'Orders'

        def method_f(m):
            if m not in methods.payement_methods:
                return '[unknown]'
            return methods.payement_methods[m].name

        self.list_fields = (
            ListFieldID(link='/admin/users/{uid}/orders/{id}'),
            ListField('Method', 'method', filter=method_f),
            ListField('Time', 'time'),
            ListField('Amount', 'amount'),
            ListField('Paid', 'paid_amount'),
            ListField('Open', 'start_date'),
            ListField('Paid?', 'paid'),
        )
        self.edit_fields = (
            EditFieldID(),
        )


class AdminProfile(AdminBaseModel):
    def __init__(self, au):
        super().__init__(parent=au, model=Profile)
        self.title = 'Profiles'

        self.list_fields = (
            ListFieldID(link='/admin/users/{uid}/profiles/{id}'),
            ListField('Name', 'name'),
        )
        self.edit_fields = (
            EditFieldID(),
        )


class AdminGiftCode(AdminBaseModel):
    def __init__(self, au=None):
        super().__init__(parent=au, model=GiftCode)
        self.title = 'Gift Codes'

        self.list_fields = (
            ListFieldID(link='/admin/giftcodes/{id}'),
            ListField('Code', 'code'),
            ListField('Time', 'time'),
            ListField('Used by', 'user'),
        )
        self.edit_fields = (
            EditFieldID(),
        )


class AdminGateway(AdminBaseModel):
    def __init__(self, au=None):
        super().__init__(parent=au, model=Gateway)
        self.title = 'Gateways'

        self.list_fields = (
            ListFieldID(link='/admin/gateways/{id}'),
            ListField('Country', 'country'),
            ListField('Name', 'name'),
            ListField('IPv4', 'ipv4'),
            ListField('IPv6', 'ipv6'),
            ListField('Enabled?', 'enabled'),
        )
        self.edit_fields = (
            EditFieldID(),
        )


class AdminStats(AdminBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'stats'
        self.title = 'Stats'

    def get(self, request):
        try:
            import pygal  # noqa
            graph = True
        except ImportError:
            request.session.flash(('error', 'Pygal not found: cannot make charts'))
            graph = False

        btcm = request.payment_methods['bitcoin']
        btcrpc = btcm.rpc
        try:
            btcd = btcrpc.getinfo()
        except (ValueError, ConnectionRefusedError):
            btcd = None

        self.main_template = 'stats.mako'
        return {'graph': graph, 'btcd': btcd}


def root_factory(request):
    return AdminRoot()


@view_config(route_name='admin_traversal', permission='admin')
def admin_traversal(context, request):
    m = request.method.lower()
    if not hasattr(context, m):
        raise HTTPMethodNotAllowed()
    c = getattr(context, m)(request)
    if isinstance(c, HTTPException):
        return c
    c['templates'] = [context.main_template] + context.templates
    c['view_context'] = context
    c['left_menu'] = context.left_menu or []
    return render_to_response('admin/layout.mako', c, request=request)


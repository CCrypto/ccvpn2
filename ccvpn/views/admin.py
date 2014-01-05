from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import func
from pyramid.httpexceptions import HTTPSeeOther, HTTPBadRequest, HTTPNotFound
from pyramid.renderers import render_to_response
from datetime import timedelta
from ccvpn.models import DBSession, User, Order, GiftCode, APIAccessToken
from ccvpn.methods import BitcoinMethod


def get_users(maxage, unit):
    q = DBSession.query(func.count(User.id).label('accounts'),
                        func.count(User.paid_until).label('paid'),
                        func.extract(unit, User.signup_date).label('time')) \
        .filter(func.age(func.now(), User.signup_date) < maxage) \
        .group_by('time').all()
    return q


@view_config(route_name='admin_graph', permission='admin')
def admin_graph(request):
    graphs = {
        'users_m': (
            'Users (month)', 'Accounts', 'Paid Acc.',
            lambda: get_users(timedelta(days=30), 'day'),
            30,
        ),
        'users_y': (
            'Users (year)', 'Accounts', 'Paid Acc.',
            lambda: get_users(timedelta(days=365), 'month'),
            12,
        ),
    }
    try:
        name = request.matchdict['name']
        import pygal
        timescale = graphs[name][4] + 1
        users_m = pygal.Line(fill=True)
        users_m.title = graphs[name][0]
        users_m.x_labels = map(str, range(0, timescale))
        users_m_q = graphs[name][3]()
        accounts_m = [0 for i in range(0, timescale)]
        paid_m = [0 for i in range(0, timescale)]
        for day in users_m_q:
            accounts_m[int(day[2])] = day[0]
            paid_m[int(day[2])] = day[1]
            print(repr(day))

        users_m.add(graphs[name][1], accounts_m)
        users_m.add(graphs[name][2], paid_m)

        return Response(users_m.render(), content_type='image/svg+xml')
    except ImportError:
        return HTTPNotFound()


@view_config(route_name='admin_home', renderer='admin/home.mako',
             permission='admin')
def admin_home(request):
    try:
        import pygal  # noqa
        graph = True
    except ImportError as e:
        print(repr(e))
        request.session.flash(('error', 'Pygal not found: cannot make charts'))
        graph = False
    btcm = BitcoinMethod()
    btcrpc = btcm.getBTCRPC(request.registry.settings)
    try:
        btcd = btcrpc.getinfo()
    except (ValueError, ConnectionRefusedError):
        btcd = None
    return {'graph': graph, 'btcd': btcd}


class AdminView(object):
    ''' Basic CRUD view for admin stuff '''
    model = None
    item_template = None
    list_template = None

    def __init__(self, request):
        self.request = request

    def tvars(self, d):
        d['request'] = self.request
        d['model'] = self.model
        d['model_name'] = self.model.__name__
        return d

    def assign_from_form(self, item):
        #item.field = self.request.field
        raise NotImplementedError()

    def post_item(self):
        if 'id' in self.request.POST and self.request.POST['id'] != '':
            item = self.get_item(self.request.POST['id'])
            item_id = self.request.POST['id']
            item = DBSession.query(self.model).filter_by(id=item_id).first()
            if not item:
                item = self.model()
                DBSession.add(item)
        else:
            item = self.model()
            DBSession.add(item)
        try:
            self.assign_from_form(item)
        except:
            DBSession.rollback()
            raise

        DBSession.commit()
        self.request.session.flash(('info', 'Saved!'))
        route_name = 'admin_' + self.model.__name__.lower() + 's'
        location = self.request.route_url(route_name, _query={'id': item.id})
        return HTTPSeeOther(location=location)

    def get_item(self, id):
        item_id = self.request.GET['id']
        item = DBSession.query(self.model).filter_by(id=item_id).first()
        template = 'admin/item.mako'
        if item is None:
            raise HTTPNotFound()
        return render_to_response(self.item_template or template,
                                  self.tvars(dict(item=item)))

    def list_items(self):
        items = DBSession.query(self.model)
        template = 'admin/list.mako'
        return render_to_response(self.list_template or template,
                                  self.tvars(dict(items=items)))

    def _get_uid(self, input):
        if input.startswith('#'):
            return input[1:]
        user = DBSession.query(User).filter_by(username=input).first()
        if not user:
            # TODO: handle that correctly
            raise HTTPBadRequest()
        return user.id

    def __call__(self):
        if self.request.method == 'POST':
            return self.post_item()
        else:
            if 'id' in self.request.GET:
                return self.get_item(self.request.GET['id'])
            else:
                return self.list_items()


@view_config(route_name='admin_users', permission='admin')
class AdminUsers(AdminView):
    model = User
    item_template = 'admin/item_user.mako'
    list_template = 'admin/list_user.mako'

    def assign_from_form(self, item):
        post = self.request.POST
        item.username = post['username']
        item.email = post['email'] or None
        if post['password']:
            item.set_password(post['password'])
        item.is_active = 'is_active' in post
        item.is_admin = 'is_admin' in post
        item.paid_until = post['paid_until'] or None


@view_config(route_name='admin_orders', permission='admin')
class AdminOrders(AdminView):
    model = Order

    def assign_from_form(self, item):
        post = self.request.POST
        item.uid = self._get_uid(post['user'])
        item.start_date = post['start_date']
        item.close_date = post['close_date'] or None
        item.amount = post['amount']
        item.paid_amount = post['paid_amount']
        item.time = post['time']
        item.method = post['method']  # TODO: permit text values
        item.paid = 'paid' in post
        item.payment = post['payment']


@view_config(route_name='admin_giftcodes', permission='admin')
class AdminGiftCodes(AdminView):
    model = GiftCode

    def assign_from_form(self, item):
        post = self.request.POST
        item.code = post['code']
        item.time = post['time']
        #item.used = self._get_uid(post['used'])


@view_config(route_name='admin_apiaccess', permission='admin')
class AdminAPIAccess(AdminView):
    model = APIAccessToken

    def assign_from_form(self, item):
        post = self.request.POST
        item.token = post['token']
        item.label = post['label']
        item.remote_addr = post['remote_addr']
        item.expire_date = post['expire_date']


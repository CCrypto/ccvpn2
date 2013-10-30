from pyramid.response import Response
from pyramid.view import view_config
from .models import DBSession, User, Order, GiftCode, APIAccessToken, Profile, random_profile_password
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func, Boolean
from pyramid.httpexceptions import HTTPOk, HTTPSeeOther, HTTPMovedPermanently, HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPUnauthorized
import markdown
import os
import re
import datetime
from pyramid.renderers import render_to_response
from . import methods
import codecs

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
               and at.remote_addr != '::ffff:'+request.remote_addr:
                return HTTPUnauthorized('remote address not allowed for this token')
            return view_func(request)
        return _func
    if function is None:
        return _dec
    else:
        return _dec(function)

@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}

@view_config(route_name='page', renderer='page.mako')
def page(request):
    path = 'ccvpn/pages/'+request.matchdict['page']+'.md'
    try:
        f = codecs.open(path, mode="r", encoding="utf-8")
        content = markdown.markdown(f.read())
        return {'content':content}
    except FileNotFoundError:
        return HTTPNotFound()

@view_config(route_name='account_login', renderer='login.mako')
def a_login(request):
    return {}

@view_config(route_name='account_login', request_method='POST', renderer='login.mako')
def a_login_post(request):
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
    return {}

@view_config(route_name='account_logout', permission='logged')
def a_logout(request):
    if 'uid' in request.session:
        del request.session['uid']
        request.session.flash(('info', 'Logged out.'))
    return HTTPSeeOther(location=request.route_url('home'))

@view_config(route_name='account_signup', renderer='signup.mako')
def a_signup(request):
    if request.method == 'POST':
        errors = []
        u = User()
        try:
            u.validate_username(request.POST['username']) or \
                errors.append('Invalid username.')
            u.validate_password(request.POST['password']) or \
                errors.append('Invalid password.')
            if request.POST['email']:
                u.validate_email(request.POST['email']) or \
                    errors.append('Invalid email address.')
            if request.POST['password'] != request.POST['password2']:
                errors.append('Both passwords do not match.')
            assert not errors
            
            nc = DBSession.query(func.count(User.id).label('nc')) \
                .filter_by(username=request.POST['username']) \
                .subquery()
            ec = DBSession.query(func.count(User.id).label('ec')) \
                .filter_by(email=request.POST['email']) \
                .subquery()
            c  = DBSession.query(nc, ec).first()
            if c.nc > 0:
                errors.append('Username already registered.')
            if c.ec > 0 and request.POST['email'] != '':
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

@view_config(route_name='account_forgot', renderer='forgot_password.mako')
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


@view_config(route_name='account', request_method='POST', permission='logged', renderer='account.mako')
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
            if DBSession.query(func.count(Profile.id)).filter_by(uid=request.user.id).scalar() > 10:
                errors.append('You have too many profiles.')
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
    

@view_config(route_name='account', permission='logged', renderer='account.mako')
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

@view_config(route_name='order_view', renderer='order.mako', permission='logged')
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
    ret = method().callback(request, o)
    DBSession.commit()
    return ret

openvpn_remote = ('gw.vpn.ccrypto.org',)
ca_content = ""

@view_config(route_name='config', permission='logged')
def config(request):
    r = render_to_response('config.ovpn.mako',
        dict(username=request.user.username,
            remotes=openvpn_remote, ca_content=ca_content,
            android='android' in request.GET))
    r.content_type = 'test/plain'
    return r

@view_config(route_name='config_profile', permission='logged')
def config_profile(request):
    pname = request.matchdict['profile']
    profile = DBSession.query(Profile) \
        .filter_by(uid=request.user.id, name=pname) \
        .first()
    if not profile:
        return HTTPNotFound()
    r = render_to_response('config.ovpn.mako',
        dict(username=request.user.username, profile=profile,
            remotes=openvpn_remote, ca_content=ca_content,
            android='android' in request.GET))
    r.content_type = 'test/plain'
    return r

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
    if not user or not user.check_password(password):
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
    return HTTPOk()

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
        return HTTPNotFound()
    # Nothing here, we do not need per-client configuration
    # Mostly for future uses (BW limit, user routes, port forwarding, ...)
    return HTTPOk()


@view_config(route_name='admin_home', renderer='admin/home.mako', permission='admin')
def admin_home(request):
    return {}

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
        route_name = 'admin_'+self.model.__name__.lower()+'s'
        return HTTPSeeOther(location=self.request.route_url(route_name, _query={'id':item.id})) # TODO fix that shit

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
        item.method = post['method'] # TODO: permit text values
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


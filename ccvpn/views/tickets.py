from sqlalchemy.orm.exc import NoResultFound
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from ccvpn.models import (
    DBSession,
    User, Profile, PasswordResetToken, Gateway, VPNSession, Order,
    Ticket, TicketMessage,
    random_access_token
)


@view_config(route_name='tickets_list', renderer='tickets/list.mako',
             permission='logged')
def tickets_list(request):
    _ = request.translate

    tickets = DBSession.query(Ticket)

    if not request.user.is_admin:
        tickets = tickets.filter_by(user_id=request.user.id)

    hide_closed = 'hide_closed' in request.GET
    if hide_closed:
        tickets = tickets.filter_by(closed=False)

    tickets = tickets.order_by(Ticket.create_date.desc()).all()

    return {'tickets': tickets, 'hide_closed': hide_closed}


@view_config(route_name='tickets_view', renderer='tickets/view.mako',
             permission='logged')
def tickets_view(request):
    _ = request.translate

    id = request.matchdict.get('id')
    try:
        ticket_q = DBSession.query(Ticket).filter_by(id=id)
        if not request.user.is_admin:
            ticket_q = ticket_q.filter_by(user_id=request.user.id)
        ticket = ticket_q.one()
    except NoResultFound:
        return HTTPNotFound()

    if request.method != 'POST':
        return {'ticket': ticket}

    redirect = HTTPSeeOther(location=request.route_url('tickets_view', id=id))

    try:
        body = request.POST['message']
        close = 'close' in request.POST
        subscribe = 'subscribe' in request.POST
    except KeyError:
        return redirect

    if body:
        errors = []

        if len(body) < 1:
            errors.append(_('Message empty'))
        if len(body) > 2000:
            errors.append(_('Message too long'))

        if errors:
            for e in errors:
                request.messages.error(e)
            return {'ticket': ticket}

        message = TicketMessage()
        message.user_id = request.user.id
        message.content = body
        message.ticket_id = ticket.id
        DBSession.add(message)

        if ticket.close:
            # We re-open it
            ticket.closed = False

        if ticket.notify_owner and ticket.user_id != message.user_id and ticket.user.email:
            mailer = get_mailer(request)
            body = render('mail/tickets_updated.mako', {
                'user': ticket.user,
                'ticket': ticket,
                'url': request.route_url('tickets_view', id=ticket.id),
            }, request=request)
            message = Message(subject=_('CCVPN: Ticket update'),
                              recipients=[ticket.user.email],
                              body=body)
            mailer.send(message)

    if request.user.id == ticket.user_id:
        ticket.notify_owner = subscribe

    if not ticket.closed and close:
        ticket.close()

    return redirect


@view_config(route_name='tickets_new', renderer='tickets/new.mako',
             permission='logged')
def tickets_new(request):
    _ = request.translate

    if request.method != 'POST':
        return {}

    try:
        subject = request.POST['subject']
        body = request.POST['message']
        subscribe = 'subscribe' in request.POST
    except KeyError:
        return {}

    errors = []

    if len(subject) < 1:
        errors.append(_('Subject empty'))
    if len(subject) > 40:
        errors.append(_('Subject too long'))

    if len(body) < 1:
        errors.append(_('Message empty'))
    if len(body) > 2000:
        errors.append(_('Message too long'))

    if errors:
        for e in errors:
            request.messages.error(e)
        return {'subject': subject, 'message': body}

    ticket = Ticket()
    ticket.user_id = request.user.id
    ticket.subject = subject
    ticket.notify_owner = subscribe

    DBSession.add(ticket)
    DBSession.flush()

    message = TicketMessage()
    message.ticket_id = ticket.id
    message.user_id = request.user.id
    message.content = body
    DBSession.add(message)

    url = request.route_url('tickets_view', id=ticket.id)
    return HTTPSeeOther(location=url)


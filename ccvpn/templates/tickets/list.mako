<%! title = 'Tickets' %>
<%inherit file="../layout.mako" />

<%
    def status(ticket):
        if ticket.closed:
            return _('Closed')

        if ticket.messages:
            last_message = ticket.messages[-1]
            if last_message.user_id == ticket.user_id:
                # Ticket owner replied
                return _('Open')

        # Staff replied
        date = last_message.create_date
        return _('Last reply: ${date}', mapping={'date': date})
%>

<section class="centeredpage">
<article>
    <h1>${_('Tickets')}</h1>

    <p><a href="/tickets/new">${_('New Ticket')}</a>
    % if hide_closed:
        - <a href="/tickets/">${_('Show closed tickets')}</a>
    % else:
        - <a href="/tickets/?hide_closed">${_('Hide closed tickets')}</a>
    % endif
    </p>

    % if tickets:
        <table class="admin-list">
            <thead>
                <tr>
                    <td>#${_('ID')}</td>
                    <td>${_('Subject')}</td>
                    <td>${_('Status')}</td>
                    % if request.user.is_support:
                        <td>${_('User')}</td>
                    % endif
                </tr>
            </thead>
            <tbody>
                % for ticket in tickets:
                    <% url = request.route_url('tickets_view', id=ticket.id) %>
                    <tr>
                        <td>#${ticket.id}</td>
                        <td><a href="${url}">${ticket.subject}</a></td>
                        <td>${status(ticket)}</td>
                        % if request.user.is_support:
                            <td><a href="${admin_url(request, ticket.user)}">${ticket.user.username}</a><a/td>
                        % endif
                    </tr>
                % endfor
            </tbody>
        </table>
    % endif
</article>
</section>


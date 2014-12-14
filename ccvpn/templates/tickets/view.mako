<%! title = 'View Ticket' %>
<%inherit file="../layout.mako" />

<section>
    <h1>Ticket: ${ticket.subject}
    % if ticket.closed:
        (${_('Closed')})
    % endif
    </h1>

    % for message in ticket.messages:
        <% owned = 'ticket-message-owned' if message.user_id == ticket.user_id else '' %>
        <article class="ticket-message ${owned}">
            <p class="ticket-message-header">
                Posted by
                % if request.user.is_support:
                    <a href="${admin_url(request, message.user)}">${message.user.username}</a>
                % else:
                    ${message.user.username}
                % endif
                
                on ${date_fmt(message.create_date)|n}.
            </p>
            <p class="ticket-message-content">
                <%! import markupsafe %>
                <% content = str(markupsafe.escape(message.content)) %>
                ${content.replace('\n', '<br />') | n}
            </p>
        </article>
    % endfor

    <article class="ticket-message-reply">
        <form class="vert" action="" method="post">
            % if ticket.closed:
                <label for="in_message">Re-open ticket:</label>
            % else:
                <label for="in_message">Reply to ticket:</label>
            % endif
            <textarea id="in_message" name="message"></textarea>

            % if not ticket.closed:
                <input type="checkbox" name="close" id="in_close" />
                <label for="in_close">${_('Close ticket')}</label>
            % endif

            % if request.user.id == ticket.user_id:
                <input type="checkbox" name="subscribe" id="in_subscribe"
                       ${'checked' if ticket.notify_owner else ''} />
                <label for="in_sub">${_('Subscribe')}</label>
            % endif

            <input type="submit" value="${_('Update')}" />
        </form>
    </article>
</section>


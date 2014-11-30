<%! title = 'Account Orders' %>
<%inherit file="layout.mako" />

<%
    def status_text(o):
        if o.paid:
            return _('Paid')

        text = _('Waiting')

        # It is possible to continue Bitcoin payments
        if order.method == order.METHOD.BITCOIN:
            url = request.route_url('order_view', hexid=hex(o.id)[2:])
            text = '<a href="{}">{}</a>'.format(url, text)

        # It can also be partially paid
        if order.paid_amount > 0:
            ptext = _('paid ${amount}', mapping={
                'amount': str(order.paid_amount) + order.currency,
            })
            text += ' (' + ptext + ')'

        return text
%>
<section id="account">
    <h1>${_('Subscription')}</h1>

    <table class="admin-list">
        <thead>
            <tr>
                <td>${_('Date')}</td>
                <td>${_('Value')}</td>
                <td>${_('Status')}</td>
            </tr>
        </thead>
        <tbody>
            % for order in orders:
                <tr>
                    <td>${order.start_date | n,date_fmt}</td>
                    <td>${order.time.days} ${_('days')}
                        (${order.amount} ${order.currency})
                    </td>
                    <td>${status_text(order) | n}</td>
                </tr>
            % endfor
        </tbody>
    </table>
    ${self.pager(page, pages)}
</section>

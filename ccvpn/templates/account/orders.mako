<%! title = 'Account Orders' %>
<%inherit file="layout.mako" />
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
                    <td>${_('Paid') if order.is_paid else _('Waiting')}</td>
                </tr>
            % endfor
        </tbody>
    </table>
    ${self.pager(page, pages)}
</section>

<%! title = 'Account Orders' %>
<%inherit file="layout.mako" />
<section id="account">
    <h1>Subscription</h1>

    <table class="admin-list">
        <thead>
            <tr>
                <td>Date</td>
                <td>Value</td>
                <td>Status</td>
            </tr>
        </thead>
        <tbody>
            % for order in orders:
                <tr>
                    <td>${order.start_date | n,date_fmt}</td>
                    <td>${order.time.days} days
                        (${order.amount} ${order.currency})
                    </td>
                    <td>${'Paid' if order.is_paid else 'Waiting'}</td>
                </tr>
            % endfor
        </tbody>
    </table>
    ${self.pager(page, pages)}
</section>

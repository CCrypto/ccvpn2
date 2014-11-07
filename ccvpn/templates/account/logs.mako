<%! title = 'Account Logs' %>
<%inherit file="layout.mako" />
<section id="account">
    <h1>${_('Logs')}</h1>

    <p>${_('Literrally <b>everything</b> we need to keep about you.') | n}</p>

    <table class="admin-list">
        <thead>
            <tr>
                <td>${_('Date')}</td>
                <td>${_('Duration')}</td>
                <td>${_('Client IP')}</td>
                <td>${_('Shared IP')}</td>
                <td>${_('Bandwidth')}</td>
            </tr>
        </thead>
        <tbody>
            % for line in logs:
                <tr>
                    <td>${line.connect_date | n,date_fmt}</td>
                    <td>${timedelta_fmt(line.duration) or _('Active') | n}</td>
                    <td>${line.internal_ip4 or '['+_('unknown')+']'}</td>
                    <td>${line.gateway.main_ip4 or '['+_('unknown')+']'}</td>
                    % if line.bytes_up and line.bytes_down:
                        <td>${line.bytes_up | n,bytes_fmt} / ${line.bytes_down | n,bytes_fmt}</td>
                    % else:
                        <td>[${_('unknown')}]</td>
                    % endif
                </tr>
            % endfor
        </tbody>
    </table>
    ${self.pager(page, pages)}
</section>

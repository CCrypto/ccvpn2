<%! title = 'Account Logs' %>
<%inherit file="layout.mako" />
<section id="account">
    <h1>Logs</h1>

    <p>Literrally <b>everything</b> we need to keep about you.</p>

    <table class="admin-list">
        <thead>
            <tr>
                <td>Date</td>
                <td>Duration</td>
                <td>Client IP</td>
                <td>Shared IP</td>
                <td>Bandwidth</td>
            </tr>
        </thead>
        <tbody>
            % for line in logs:
                <tr>
                    <td>${line.connect_date | n,date_fmt}</td>
                    <td>${timedelta_fmt(line.duration) or 'Active' | n}</td>
                    <td>${line.internal_ip4 or '[unknown]'}</td>
                    <td>${line.gateway.main_ip4 or '[unknown]'}</td>
                    % if line.bytes_up and line.bytes_down:
                        <td>${line.bytes_up | n,bytes_fmt} / ${line.bytes_down | n,bytes_fmt}</td>
                    % else:
                        <td>[unknown]</td>
                    % endif
                </tr>
            % endfor
        </tbody>
    </table>
    ${self.pager(page, pages)}
</section>

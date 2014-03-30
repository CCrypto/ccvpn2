<%! title = 'Gateways' %>
<%inherit file="layout.mako" />
<section id="gateways">
    <article>
    <h1>Status</h1>

    <h2>Stats</h2>
    <ul>
        <li>We have ${n_users} active users.</li>
        <li>We provide ${len(gateways)} servers in ${n_countries} countries,
            and a total bandwidth of <b>${total_bw}</b></li>
    </ul>
    % if bw_graph:
        <a href="${bw_graph[0]}">
            <img src="${bw_graph[1]}" alt="Network bandwidth graph" />
        </a>
    % endif

    <h2>Gateways</h2>
        <p><code>gw.204vpn.net</code> will always point to a random and working server.<br />
           <code>[country].204vpn.net</code> is a random server in a given country. (e.g. fr.204vpn.net)</p>
        % if gateways:
        <table>
            <thead>
                <tr><td>Host</td> <td>ISP / Bandwidth</td> <td>Location</td> <td>Uptime <span class="td-info">on 31 days</span></td></tr>
            </thead>
            <tbody>
                % for d in gateways:
                <tr><td class="host_line">
                        <span class="host_name">${d.host_name}</span>
                    </td>
                    <td><a href="${d.isp_url}">${d.isp_name}</a> /
                        ${d.bps_formatted}</td>
                    <td>${d.country.upper()}</td>
                    <td>${d.uptime}%</td>
                </tr>
                % endfor
            </tbody>
        </table>
        % endif
    </article>

    <script type="text/javascript" src="/static/ping.js"></script>

    <div style="clear: both"></div>
</section>

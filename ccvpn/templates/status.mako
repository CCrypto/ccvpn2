<%! title = 'Status' %>
<%inherit file="layout.mako" />
<section id="gateways">
    <article>
    <h1>${_('Status')}</h1>

    <h2>${_('Stats')}</h2>
    <ul>
        <li>${_('We have ${n} active users.', mapping={'n': n_users})}
            ${_('${n} are using the VPN right now.', mapping={'n': n_connected})}</li>
        <li>${_('We provide ${ns} servers in ${nc} countries,',
                mapping={'ns': len(gateways), 'nc': n_countries})}
            ${_('and a total bandwidth of ${bw}', mapping={'bw': total_bw})}</li>
    </ul>
    % if bw_graph:
        <a href="${bw_graph[0]}">
            <img src="${bw_graph[1]}" alt="${_('Network bandwidth graph')}" />
        </a>
    % endif

    <h2>${_('Gateways')}</h2>
        <p><code>gw.random.204vpn.net</code> ${_('points to a random server.')}<br />
           <code>gw.[country].204vpn.net</code> ${_('to a random server in a given country.')}
           ${_('(e.g. ${e})', mapping={'e': 'gw.fr.204vpn.net'})}</p>
        % if gateways:
        <table>
            <thead>
                <tr><td>${_('Host')}</td>
                    <td>${_('ISP')} / ${_('Bandwidth')}</td>
                    <td>${_('Location')}</td>
                    <td>${_('Uptime')} <span class="td-info">${_('on 31 days')}</span></td>
                </tr>
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
</section>

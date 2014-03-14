<%! title = 'Gateways' %>
<%inherit file="layout.mako" />
<section id="gateways">
    <article>
    <h1>Gateways</h1>
        <p><b>gw.204vpn.net</b> will always point to a random and working server.<br />
           <b>[country].204vpn.net</b> is a random server in a given country. (e.g. fr.204vpn.net)</p>

        <table>
            <thead>
                <tr><td>Host</td> <td>ISP</td> <td>Location</td> <td>Uptime</td></tr>
            </thead>
            <tbody>
                % for h, d in gateways.items():
                <tr><td class="host_line"><span class="host_name">${h}</span> </td>
                    % if isinstance(d['isp'], str):
                        <td>${d['isp']}</td>
                    % else:
                        <td><a href="${d['isp'][1]}">${d['isp'][0]}</a></td>
                    % endif
                    <td>${d['loc']}</td>
                    <td>${d['uptime']}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </article>

    <script type="text/javascript" src="/static/ping.js"></script>
    
    <div style="clear: both"></div>
</section>

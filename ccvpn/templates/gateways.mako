<%inherit file="layout.mako" />
<section id="gateways">
    <h2>Gateways</h2>
    <article>
        <table>
            <thead>
                <tr><td>Host</td> <td>ISP</td> <td>Location</td> <td>Uptime</td></tr>
            </thead>
            <tbody>
                % for h, d in gateways.items():
                <tr><td>${h}</td>
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
    
    <div style="clear: both"></div>
</section>

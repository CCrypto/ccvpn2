<%inherit file="../layout.mako" />

<section>
    <h2>Admin - Home</h2>
    <article>
        <ul>
            <li><a href="/admin/users">Users</a></li>
            <li><a href="/admin/orders">Orders</a></li>
            <li><a href="/admin/giftcodes">Gift Codes</a></li>
            <li><a href="/admin/apiaccess">API Access Tokens</a></li>
        </ul>
    </article>
    <article>
        % if btcd:
            <p>Bitcoind:
                balance: ${btcd.balance},
                blocks: ${btcd.blocks}
            </p>
        % else:
            <p>Bitcoind: <b>Failed to get infos</b></p>
        %endif
    </article>
    % if graph:
        <img src="/admin/graph/users_m.svg" height="49%" width="49%" />
        <img src="/admin/graph/users_y.svg" height="49%" width="49%" />
    % endif
    <div style="clear: both"></div>
</section>

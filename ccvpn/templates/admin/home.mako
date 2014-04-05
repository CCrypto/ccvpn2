<%inherit file="../layout.mako" />

<section>
    <h2>Admin - Home</h2>
    <article>
        <ul>
            <li><a href="/admin/users">Users</a></li>
            <li><a href="/admin/orders">Orders</a></li>
            <li><a href="/admin/giftcodes">Gift Codes</a></li>
            <li><a href="/admin/apiaccesstokens">API Access Tokens</a></li>
            <li><a href="/admin/gateways">Gateways</a></li>
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
        <figure><embed src="/admin/graph/users.svg?period=m" /></figure>
        <figure><embed src="/admin/graph/users.svg?period=y" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=m&amp;method=0" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=y&amp;method=0" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=m&amp;method=1" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=y&amp;method=1" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=m&amp;method=2" /></figure>
        <figure><embed src="/admin/graph/income.svg?period=y&amp;method=2" /></figure>
    % endif
    <div style="clear: both"></div>
</section>

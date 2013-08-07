<%inherit file="layout.mako" />

<section id="account">
    <h2>Order #${o.id}</h2>

% if o.paid:
    <article>
        <p>Thank you for using our VPN!<br />
        Now, read our <a href="/page/docs">installation howtos</a> to start
        using it or <a href="/page/support">ask the support</a> if you need help.</p>
    </article>
% else:
    <article>
    % if o.method == o.METHOD.BITCOIN:
        <p>Please send <b>${o.amount - o.paid_amount} BTC</b> to
            <b>${o.payment['btc_address']}</b> .</p>
        <p>This page is updated every 5 minutes.<p>
    % elif o.method == o.METHOD.PAYPAL:
        <p>If you already paid with Paypal, please wait for Paypal to confirm
            the transaction, it can take up to 30 minutes.</br>
    % endif
    </article>
% endif
    
    <div style="clear: both"></div>
</section>


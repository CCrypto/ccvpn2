<%inherit file="layout.mako" />

<%def name="autorefresh()">
    <p>This page is updated every minute.</p>
    <script type="text/javascript">
        window.onload = function() {
            setTimeout(function() {
                location.reload(false);
            }, 60 * 1000);
        }
    </script>
</%def>

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
        <p>Please send <b>${o.amount - o.paid_amount} BTC</b>
            to <b>${o.payment['btc_address']}</b> .</p>
        ${autorefresh()}
    % elif o.method == o.METHOD.PAYPAL:
        <p>If you already paid with Paypal, please wait for Paypal to confirm
            the transaction, it can take up to 30 minutes.</p>
        ${autorefresh()}
    % elif o.method == o.METHOD.STRIPE:
        <form action="/order/callback/${'%x' % o.id}" method="POST">
            <script
                src="https://checkout.stripe.com/checkout.js" class="stripe-button"
                data-key="${pkey}"
                data-amount="${amount}"
                data-currency="${currency}"
                data-name="${name}"
                data-description="${description}">
            </script>
            <noscript>
                <p>You need JavaScript to use Stripe.</p>
            </noscript>
        </form>
    % endif
    </article>
% endif
    
    <div style="clear: both"></div>
</section>


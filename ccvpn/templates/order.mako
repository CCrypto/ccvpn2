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
    <h2>${_('Order')} #${o.id}</h2>

% if o.paid:
    <article>
        <p>${_('Thank you for using our VPN!')}<br />
        ${_('Now, read our')} <a href="/page/help">${_('installation howtos')}</a>
        ${_('to start using it or')} <a href="/page/support">${_('ask the support')}</a>
        ${_('if you need help.')}</p>
    </article>
% else:
    <article>
    % if o.method == o.METHOD.BITCOIN:
        <p>${_('Please send ${n} BTC to ${a}.',
               mapping={'n': o.amount - o.paid_amount, 'a': o.payment['btc_address']})}
        </p>
        ${autorefresh()}
    % elif o.method == o.METHOD.PAYPAL:
        <p>${_('help_paypal_wait')}</p>
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
                <p>${_('You need JavaScript to use Stripe.')}</p>
            </noscript>
        </form>
    % endif
    </article>
% endif
</section>


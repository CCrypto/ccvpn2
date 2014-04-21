<%inherit file="layout.mako" />

<section>
% if motd:
<article class="home-motd">
    <p>${motd | n}</p>
</article>
% endif

<article id="homepage">
    <div class="homeitem">
        <img src="/static/unlimited.svg" alt="" />
        <h2>${_('Unlimited')}</h2>
        <p><b>${_('Unlimited bandwidth')}</b>.<br />
            <b>${_('Uncensored')}</b>.<br />
            ${_('We have porn and pirates.')}</p>
    </div>

    <div class="homeitem">
        <img src="/static/cheap.svg" alt="" />
        <h2>${_('Cheap')}</h2>
        <p><b>${eur_price}&euro; / ${btc_price}BTC</b> ${_('per month!')}<br/>
            ${_('We accept Paypal, Bitcoins and Stripe.')}</p>
    </div>

    <div class="homeitem">
        <img src="/static/anon.svg" alt="" />
        <h2>${_('Secure')}</h2>
        <p><b>${_('Encrypted tunnel')}</b>
            ${_('with an <b>anonymous address</b>.')|n}<br />
            ${_('Supports DNSSEC and PFS.')}</p>
    </div>

    <div class="homeitem">
        <img src="/static/openvpn.svg" alt="" />
        <h2>${_('OpenVPN')}</h2>
        <p>${_('Secure, Free, easy to use. On:')}<br/>
            <ul>
                <li><b>Windows, OSX</b></li>
                <li><b>GNU/Linux, BSD</b></li>
                <li><b>Android, iOS</b></li>
            </ul>
        </p>
    </div>

    <div class="homeitem">
        <img src="/static/fast.svg" alt="" />
        <h2>${_('Fast')}</h2>
        <p><b>1Gbps</b><br/>
            <b>${_('Compressed tunnel.')}</b><br />
            ${_('Even on Youtube.')}
        </p>
    </div>

    <div style="clear: both"></div>
</article>
</section>

<p id="homecreate">
    <a href="/account/signup">${_('Sign up')}</a>
</p>

<section>
    <article class="homehalf">
        <h2>${_('Why?')}</h2>
        <ul>
            <li>${_('Hide any personal data found from your IP address')}</li>
            <li>${_('Protect your privacy on open networks')}</li>
            <li>${_('Compress traffic on slow connections')}</li>
            <li>${_('Bypass restrictive firewalls')}</li>
            <li>${_('Enable IPv6 on IPv4-only networks')}</li>
        </ul>
    </article>
    <article class="homehalf">
        <h2>${_('Free Trial!')}</h2>
        <p>${_('Try the VPN for 7 days for free!')}<br />
            <a href="/account/signup">${_('Sign up and ask for a free account')}</a>.</p>
</section>



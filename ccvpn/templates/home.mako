<%inherit file="layout.mako" />

<section>
<article id="homepage">
    <div class="homeitem">
        <img src="/static/unlimited.svg" alt="" />
        <h2>Unlimited</h2>
        <p><b>Unlimited bandwidth</b>.<br />
            <b>Uncensored</b>.<br />
            We have porn and pirates.</p>
    </div>

    <div class="homeitem">
        <img src="/static/cheap.svg" alt="" />
        <h2>Cheap</h2>
        <p><b>${eur_price}€ / ${btc_price}BTC</b> per month!<br/>
            We accept Paypal and Bitcoins</p>
    </div>

    <div class="homeitem">
        <img src="/static/anon.svg" alt="" />
        <h2>Secure</h2>
        <p>Provides an <b>encrypted</b> tunnel<br />
            with an <b>anonymous</b> address.<br />
            Supports <b>DNSSEC</b> and <b>PFS</b>.</p>
    </div>

    <div class="homeitem">
        <img src="/static/openvpn.svg" alt="" />
        <h2>OpenVPN</h2>
        <p>Secure, Free, easy to use. On:<br/>
            <ul>
                <li><b>Windows, OSX</b></li>
                <li><b>GNU/Linux, BSD</b></li>
                <li><b>Android, iOS</b></li>
            </ul>
        </p>
    </div>

    <div class="homeitem">
        <img src="/static/fast.svg" alt="" />
        <h2>Fast</h2>
        <p><b>1Gbps</b><br/>
            <b>Compressed</b> tunnel.<br />
            Even on <b>Youtube</b>.
        </p>
    </div>

    <div style="clear: both"></div>
</article>
</section>

<p id="homecreate">
    <a href="/account/signup">Sign up</a>
</p>

<section>
    <article class="homehalf">
        <h2>Why?</h2>
        <ul>
            <li>Hide any personal data found from your IP address</li>
            <li>Protect your privacy on open networks</li>
            <li>Compress traffic on slow connections</li>
            <li>Bypass restrictive firewalls</li>
            <li>Enable IPv6 on IPv4-only networks</li>
        </ul>
    </article>
    <article class="homehalf">
        <h2>Free Trial!</h2>
        <p>Try the VPN for 7 days for free!<br />
            <a href="/account/signup">Sign up</a> and ask for a free account</p>
</section>



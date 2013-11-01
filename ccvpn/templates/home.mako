<%inherit file="layout.mako" />

<section id="homepage">
    <article class="home-unlimited-a">
        <img src="/static/unlimited.svg" alt="" />
        <h2>Unlimited</h2>
        <p><b>Unlimited bandwidth</b>.<br />
            <b>Uncensored</b>.<br />
            We have porn and pirates.</p>
    </article>

    <article>
        <img src="/static/cheap.svg" alt="" />
        <h2>Cheap</h2>
        <p><b>${eur_price}€ / ${btc_price}BTC</b> per month!<br/>
            We accept Paypal and Bitcoins</p>
    </article>

    <article>
        <img src="/static/anon.svg" alt="" />
        <h2>Secure</h2>
        <p>Provides an <b>encrypted</b> tunnel<br />
            with an <b>anonymous</b> address.<br />
            Supports <b>DNSSEC</b> and <b>PFS</b>.</p>
    </article>

    <article>
        <img src="/static/openvpn.svg" alt="" />
        <h2>OpenVPN</h2>
        <p>Secure, Free, easy to use. On:<br/>
            <ul>
                <li><b>Windows, OSX</b></li>
                <li><b>GNU/Linux, BSD</b></li>
                <li><b>Android, iOS</b></li>
            </ul>
        </p>
    </article>

    <article>
        <img src="/static/fast.svg" alt="" />
        <h2>Fast</h2>
        <p><b>100Mbps</b><br/>
            Even on Youtube.
        </p>
    </article>

    <div style="clear: both"></div>
</section>
<section id="homecreate">
    <a href="/account/signup">Sign up</a>
</section>



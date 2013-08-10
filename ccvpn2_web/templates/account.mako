<%inherit file="layout.mako" />
<%
    user = request.user
    profiles = request.user.profiles
%>
<section id="account">
    <h2>Account : ${user.username}</h2>
    % if user.is_paid:
        <article>
            <p>Your account is <b>paid</b> for ${user.paid_days_left()} day(s).</p>
            <ul>
                <li>Default profile: [Ask password] <a href="/account/config/0/">Get ccrypto.ovpn</a></li>
            % for profile in profiles:
                <li>Profile : ${profile.name}
                - <form class="profileform" method="post" action="/account/">
                    <input type="hidden" name="profiledelete" value="${profile.id}" />
                    <input type="submit" class="deletebutton" value="Delete" />
                </form>
                - <a href="/config/${profile.id}/">Get ccrypto.ovpn</a></li>
            % endfor
                <li>
                    Add : 
                    <form class="profileform" action="/account/" method="post">
                        <input type="text" name="profilename" id="fp_name" placeholder="Profile name" />
                        <input type="checkbox" value="1" name="askpw" id="fp_askpw" checked="checked" />
                        <label for="fp_askpw">Ask password?</label>
                        <input type="submit" />
                    </form>
                </li>
            </ul>
            <p>You can only have <b>one connection per profile</b>,
                but up to 10 profiles. (10 running clients)<br />
                "Ask password" will ask password when connecting.
                If you uncheck it, the config file will incllude a random
                private key.</p>
        </article>
    % endif

    <article class="two">
        <h3>Settings</h3>
        <form action="/account/" method="post">
            <label for="ins_password">Change password</label>
            <input type="password" id="ins_password" name="password" />

            <label for="ins_password2">Change password (repeat)</label>
            <input type="password" id="ins_password2" name="password2" />

            <label for="ins_email">E-mail</label>
            <input type="email" id="ins_email" name="email" value="${email or ''}" />
            
            <input type="submit" />
        </form>
    </article>
    <article class="two">
        <h3>Renew</h3>
        <form action="/order/" method="post">
            <div class="inlinefield">
            <label for="ino_time">Time</label>
            <select id="ino_time" name="time">
                <option value="1">1 month</option>
                <option value="3">3 months</option>
                <option value="6">6 months</option>
                <option value="12">12 months</option>
            </select>
            </div>
            
            <div class="inlinefield">
            <label for="ino_method">Method</label>
            <select id="ino_method" name="method">
                <option value="paypal">Paypal</option>
                <option value="bitcoin">Bitcoin</option>
            </select>
            </div>

            <div style="clear:both"></div>

            <p>-- or --</p>
            <label for="ins_code">Gift code</label>
            <input type="text" id="ins_code" name="code" pattern="[A-Z0-9]{1,16}" autocomplete="off" />

            <input type="submit" />
        </form>
    </article>
    
    <div style="clear: both"></div>
</section>

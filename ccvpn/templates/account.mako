<%! title = 'Account' %>
<%inherit file="layout.mako" />
<%
    user = request.user
    profiles = request.user.profiles
%>
<section id="account">
    <h1>Account : ${user.username}</h1>

    <article class="account-box">
        % if user.is_paid:
            <p>Your account is <b>paid for ${user.paid_days_left()} day(s)</b>.</p>
        % else:
            <p>Your account is <b>not paid</b>.</p>
            % if len(user.paid_orders) == 0:
            <p>You can request a free 4 days trial <a href="/page/support">here</a></p>
            % endif
            <hr />
        % endif
        <form action="/order/" method="post" class="inline">
            <label for="ino_time">Add</label>
            <select id="ino_time" name="time">
                <option value="1">1 month</option>
                <option value="3">3 months</option>
                <option value="6">6 months</option>
                <option value="12">12 months</option>
            </select>
            <label for="ino_method">with</label>
            <select id="ino_method" name="method">
                <option value="paypal">Paypal</option>
                <option value="bitcoin">Bitcoin</option>
            </select>
            <input type="submit" value="Add" />
        </form>
        <form action="/order/" method="post" class="inline">
            <input type="text" id="ins_code" name="code" maxlength="16"
                   pattern="[a-zA-Z0-9]{1,16}" autocomplete="off" />
            <input type="submit" value="Use gift code" />
        </form>
    </article>

    % if user.is_paid:
    <article>
        <ul>
            <li>You can only have <b>one connection per profile</b>,
                but up to 10 profiles. (10 running clients)</li>
            <li>To use a profile, download the right config and <b>use
                "name/profile" as your VPN username.</b></li>
            <li>TCP is slower. Use it only if you have important packet
                loss or a restrictive firewall.</li>
        </ul>

        <h3>Download config</h3>
        <form action="/config/ccrypto.ovpn" method="get" class="largeform">
            <label for="gc_username">Profile</label>
            <select name="pname" id="gc_username">
                <option value="" selected>${user.username} [default]</option>
                % for profile in profiles:
                    <option value="${profile.name}">${user.username}/${profile.name}</option>
                % endfor
            </select>

            <label for="gc_os">OS</label>
            <select name="os" id="gc_os">
                <option value="windows">Windows</option>
                <option value="android">Android</option>
                <option value="ubuntu">Ubuntu</option>
                <option value="osx">OS X</option>
                <option value="other-gnulinux">Other / GNU/Linux</option>
            </select>

            <label for="gc_gw">Gateway</label>
            <select name="gw" id="gc_gw">
                <option value="" selected>Random</option>
                % for country in gw_countries:
                    <option value="rr_${country}">Country: ${country.upper()}</option>
                % endfor
            </select>

            <label for="gc_ftcp">Force TCP</label>
            <input type="checkbox" name="forcetcp" id="gc_ftcp" />

            <input type="submit" value="Get config" />
        </form>

        <h3>Manage Profiles</h3>
        <form class="profileform" action="/account/" method="post">
            <p>
            <input type="text" name="profilename" id="fp_name" placeholder="Profile name" pattern="[a-zA-Z0-9]{1,16}" />
            <input type="submit" value="Add" />
            </p>
        </form>
        % if profiles:
        <form class="profileform" action="/account/" method="post">
            <p>
            <select name="profiledelete">
                % for profile in profiles:
                    <option value="${profile.id}">${user.username}/${profile.name}</option>
                % endfor
            </select>
            <input type="submit" value="Delete" />
            </p>
        </form>
        % endif
    </article>
    % endif

    <article class="account-box">
        <% url = 'http://vpn.ccrypto.org/?ref=' + str(request.user.id) %>
        <p>Get two weeks for free for every referral that takes at least one
        month!<br />
        Share this link: <input type="text" size="30" value="${url}" />
        </p>
    </article>
</section>


<section>
    <article class="homehalf">
        <h2>Settings</h2>
        <form action="/account/" method="post" class="vert">
            <label for="ins_password">Change password</label>
            <input type="password" id="ins_password" autocomplete="off" name="password" />

            <label for="ins_password2">Change password (repeat)</label>
            <input type="password" id="ins_password2" autocomplete="off" name="password2" />

            <label for="ins_email">E-mail</label>
            <input type="email" id="ins_email" name="email" autocomplete="off" value="${email or ''}" />
            
            <input type="submit" value="SAVE" />
        </form>
    </article>
</section>

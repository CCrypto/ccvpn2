<%inherit file="layout.mako" />
<%
    user = request.user
    profiles = request.user.profiles
%>
<section id="account">
    <h1>Account : ${user.username}</h1>

    <article class="account-box">
        <% url = 'http://vpn.ccrypto.org/?ref=' + str(request.user.id) %>
        <p>Get two weeks for free for every referral that takes at least one
        month!<br />
        Share this link: <input type="text" size="30" value="${url}" />
        </p>
    </article>

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
            <table>
                <tr><td>Profile: <b>${user.username}</b></td>
                    <td>[default]</td>
                    <td><a href="/config/ccrypto.ovpn"><b>Get config</b></a></td>
                    <td><a href="/config/ccrypto.ovpn?android"><b>(For Android)</b></a></td>
                </tr>
            % for profile in profiles:
                <tr><td>Profile: <b>${user.username}/${profile.name}</b></td>
                    <td><form class="profileform" method="post" action="/account/">
                        <input type="hidden" name="profiledelete" value="${profile.id}" />
                        <input type="submit" class="deletebutton" value="Delete" />
                    </form></td>
                    <td><a href="/config/ccrypto-${profile.name}.ovpn"><b>Get config</b></a></td>
                    <td><a href="/config/ccrypto-${profile.name}.ovpn?android"><b>(For Android)</b></a></td>
                    </tr>
            % endfor
            </table>

            <form class="profileform" action="/account/" method="post">
                <p>
                <input type="text" name="profilename" id="fp_name" placeholder="Profile name" pattern="[a-zA-Z0-9]{1,16}" />
                <input type="submit" value="Add" />
                </p>
            </form>

            <ul class="account-box">
                <li>You can only have <b>one connection per profile</b>,
                    but up to 10 profiles. (10 running clients)</li>
                <li>To use a profile, download the right config and use
                    its identifier as your VPN username.</li>
            </ul>
            <hr />
        </article>
    % endif

    <article class="two">
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

    <div style="clear: both"></div>
</section>

<%! title = 'Account' %>
<%inherit file="layout.mako" />
<%
    user = request.user
    profiles = request.user.profiles
%>
<section id="account">
    <h1>${_('Account')} : ${user.username}</h1>

    <article class="account-box">
        % if user.is_paid:
            <p>${_('Your account is paid for ${time} day(s).',
                   mapping={'time': user.paid_days_left()})}</p>
        % else:
            <p>${_('Your account is not paid.')}</p>
            % if len(user.paid_orders) == 0:
            <p>${_('You can request a free 7 days trial here')}:
                <a href="/page/support">${_('Support')}</a></p>
            % endif
            <hr />
        % endif
        <form action="/order/" method="post" class="inline">
            <label for="ino_time">${_('Add')}</label>
            <select id="ino_time" name="time">
                <option value="1">1 ${_('month')}</option>
                <option value="3">3 ${_('months')}</option>
                <option value="6">6 ${_('months')}</option>
                <option value="12">12 ${_('months')}</option>
            </select>
            <label for="ino_method">${_('with')}</label>
            <select id="ino_method" name="method">
                <option value="stripe">Stripe (${_('credit card')})</option>
                <option value="paypal">Paypal</option>
                <option value="bitcoin">Bitcoin</option>
                % if request.user.is_admin:
                    <option value="admin">Admin awesomeness</option>
                % endif
            </select>
            <input type="submit" value="${_('Add')}" />
        </form>
        <form action="/order/" method="post" class="inline">
            <input type="text" id="ins_code" name="code" maxlength="16"
                   pattern="[a-zA-Z0-9]{1,16}" autocomplete="off" />
            <input type="submit" value="${_('Use gift code')}" />
        </form>
    </article>

    % if user.is_paid:
    <article>
        <ul>
            <li>${_('help_connection_limit')}</li>
            <li>${_('help_profile_usage')}</li>
            <li>${_('help_tcp_usage')}</li>
        </ul>

        <h3>${_('Download config')}</h3>
        <form action="/config/ccrypto.ovpn" method="get" class="largeform">
            <label for="gc_username">${_('Profile')}</label>
            <select name="pname" id="gc_username">
                <option value="" selected>${user.username} [${_('default')}]</option>
                % for profile in profiles:
                    <option value="${profile.name}">${user.username}/${profile.name}</option>
                % endfor
            </select>

            <label for="gc_os">${_('OS')}</label>
            <select name="os" id="gc_os">
                <option value="windows">Windows</option>
                <option value="android">Android</option>
                <option value="ubuntu">Ubuntu</option>
                <option value="osx">OS X</option>
                <option value="freebox">Freebox</option>
                <option value="other-gnulinux">${_('Other')} / GNU/Linux</option>
            </select>

            <label for="gc_gw">${_('Gateway')}</label>
            <select name="gw" id="gc_gw">
                <option value="" selected>${_('Random')}</option>
                % for country in gw_countries:
                    <option value="rr_${country}">${_('Country')}:
                        ${country.upper()}</option>
                % endfor
            </select>

            <label for="gc_ftcp">${_('Force TCP')}</label>
            <input type="checkbox" name="forcetcp" id="gc_ftcp" />

            <label for="gc_ipv6">${_('Enable IPv6')}</label>
            <input type="checkbox" name="enable_ipv6" id="gc_ipv6" checked="checked" />

            <input type="submit" value="${_('Get config')}" />
        </form>

        <h3>${_('Manage Profiles')}</h3>
        <form class="profileform" action="/account/" method="post">
            <p>
            <input type="text" name="profilename" id="fp_name" placeholder="${_('Profile name')}" pattern="[a-zA-Z0-9]{1,16}" />
            <input type="submit" value="${_('Add')}" />
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
            <input type="submit" value="${_('Delete')}" />
            </p>
        </form>
        % endif
    </article>
    % endif

    <article class="account-box">
        <% url = 'http://vpn.ccrypto.org/?ref=' + str(request.user.id) %>
        <p>${_('help_ref')}<br />
        ${_('Share this link')}: <input type="text" size="30" value="${url}" />
        </p>
    </article>
</section>


<section>
    <article class="homehalf">
        <h2>${_('Settings')}</h2>
        <form action="/account/" method="post" class="vert">
            <label for="ins_password">${_('Change password')}</label>
            <input type="password" id="ins_password" autocomplete="off" name="password" />

            <label for="ins_password2">${_('Change password')} (${_('repeat')})</label>
            <input type="password" id="ins_password2" autocomplete="off" name="password2" />

            <label for="ins_email">${_('E-mail')}</label>
            <input type="email" id="ins_email" name="email" autocomplete="off" value="${email or ''}" />
            
            <input type="submit" value="${_('Save')}" />
        </form>
    </article>
</section>

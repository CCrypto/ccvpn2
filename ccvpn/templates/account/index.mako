<%! title = 'Account' %>
<%inherit file="layout.mako" />
<%
    user = request.user
    profiles = request.user.profiles
%>
<section id="account">
    <h1>${_('Account')} : ${user.username}</h1>

    % if user.is_paid:
        <p>${_('Your account is paid until ${until}. (${time} day(s) left)',
               mapping={'until': user.paid_until.strftime('%Y-%m-%d'),
                        'time': user.paid_days_left()})}</p>
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

    <article class="account-box">
        <p>${_('help_ref')}<br />
        ${_('Share this link')}: <input type="text" size="30" value="${ref_url}" />
        <a target="_blank"
           href="${twitter_link}">${_('Share on Twitter')}</a>
        </p>
    </article>

    <hr />

    <h2>${_('Profiles')}</h2>

    <p>${_('help_connection_limit')}</p>

    % if profiles:
        % for profile in profiles:
            <article class="profile">
                <h2>${_('VPN username')}: ${request.user.username}/${profile.name}</h2>
                <ul>
                    <li>${_('Gateway')}:
                        % if profile.gateway_country:
                            ${_('Only in country')} ${profile.gateway_country.upper()}
                        % elif profile.gateway_id:
                            ${_('Only')} ${profile.gateway}
                        % else:
                            ${_('Random')}
                        % endif
                        % if profile.force_tcp:
                            [${_('TCP only')}]
                        % endif
                        </li>
                    <li>${_('OS')}: ${profile.client_os or _('Not set')}
                        % if profile.disable_ipv6:
                            [${_('IPv6 disabled')}]
                        % endif
                    </li>
                    % if profile.use_http_proxy:
                        <li>${_('Use HTTP proxy')}: ${profile.use_http_proxy}</li>
                    % endif
                </ul>

                <%
                    rurl = request.route_url
                    edit_url = rurl('account_profiles_edit', id=profile.id)
                    del_url = rurl('account')
                    dl_url = rurl('config', username=profile.user.username,
                                                     pname=profile.name)
                %>

                <!-- delete button -->
                <form action="${del_url}" method="POST">
                    <input type="hidden" name="delete" value="${profile.id}" />
                    <input type="submit" value="${_('Delete')}" />
                </form>

                <!-- edit button -->
                <form action="${edit_url}" method="GET">
                    <input type="submit" value="${_('Edit')}" />
                </form>

                <!-- download link -->
                <a href="${dl_url}"><b>${_('Download config file')}</b></a>
                ### TODO: wget-able DL url
            </article>
        %endfor
        % if len(profiles) < limit:
            <h3>${_('Add Profile')}</h3>
            <form class="inline" action="${request.route_url('account')}" method="post">
                <p>
                <input type="text" name="profilename" id="fp_name"
                       placeholder="${_('Profile name')}" pattern="[a-zA-Z0-9]{1,16}" />
                <input type="submit" value="${_('Add')}" />
                </p>
            </form>
        % endif
    % else:
        <p>${_('You have no profiles for now. Create one to start using the VPN')}:</p>
            <form class="inline" action="${request.route_url('account')}" method="post">
                <p>
                <input type="text" name="profilename" id="fp_name"
                       placeholder="${_('Profile name')}" pattern="[a-zA-Z0-9]{1,16}" />
                <input type="submit" value="${_('Add')}" />
                </p>
            </form>
    % endif

</section>


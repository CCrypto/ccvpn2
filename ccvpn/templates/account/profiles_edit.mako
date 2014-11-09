<%! title = 'Account Profile' %>
<%inherit file="layout.mako" />
<section id="account">
    <h1>Profile: ${profile.name}</h1>

    <form action="${edit_post_url}" method="post" class="largeform">
        % if profile.name:
            ## Only show name if it's not the default profile
            <label for="p_name">${_('Profile Name')}</label>
            <input type="text" name="name" value="${profile.name}" />
        % endif

        <label for="p_os">${_('OS')}</label>
        <select name="client_os" id="p_os">
            % for k, v in profile.CLIENT_OS.items():
                <option value="${k}"
                % if profile.client_os == k:
                    selected="selected"
                % endif
                >${v}</option>
            % endfor
        </select>

        <label for="p_gw">${_('Gateway')}</label>
        <select name="gateway" id="p_gw">
            <option value="" selected>${_('Random')}</option>
            % for country in gw_countries:
                <option value="rr_${country}"
                % if profile.gateway_country == country:
                    selected="selected"
                % endif
                >${_('Country')}:
                    ${country.upper()}</option>
            % endfor
        </select>

        <label for="p_proto">${_('Protocol')}</label>
        <select name="protocol" id="p_proto">
            % for key, value in profile.PROTOCOLS.items():
                <option value="${key}"
                % if profile.protocol == key:
                    selected="selected"
                % endif
                >${value}</option>
            % endfor
        </select>
        <p class="inputinfo">${_('help_tcp_usage')}</p>

        <label for="p_ipv6">${_('Enable IPv6?')}</label>
        <input type="checkbox" name="enable_ipv6" id="p_ipv6"
               ${'checked="checked"' if not profile.disable_ipv6 else ''}/>
        
        <label for="p_proxy">${_('Use HTTP Proxy?')}</label>
        <input type="text" name="use_http_proxy" id="p_proxy" value="${profile.use_http_proxy or ''}" />

        <input type="submit" value="${_('Save profile')}" />
    </form>
</section>



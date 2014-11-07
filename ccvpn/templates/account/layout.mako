<%inherit file="../layout.mako" />
<%
    left_menu = [
        ('/account/', _('Account')),
        ('/account/settings', _('Settings')),
        #('/account/profiles', 'Profiles'),
        None,
        ('/account/orders', _('Subscription')),
        ('/account/logs', _('VPN Logs')),
    ]
%>
<section>
    <div class="left_menu">
        <p class="title"><a href="/account/">${_('Account')}</a></p>
        <ul>
            % for lmi in left_menu:
                % if lmi is None:
                    <li class="separator"></li>
                % else:
                    <li><a href="${lmi[0]}">${lmi[1]}</a></li>
                % endif
            % endfor
        </ul>
    </div>
    <article>
        ${next.body()}
    </article>
</section>



<%! title = 'Account Settings' %>
<%inherit file="layout.mako" />
<% user = request.user %>
<section id="account">
    <h1>${_('Settings')}</h1>

    <form action="/account/settings" method="post" class="vert">
        <label for="ins_password">${_('Change password')}</label>
        <input type="password" id="ins_password" autocomplete="off" name="password" />

        <label for="ins_password2">${_('Change password')} (${_('repeat')})</label>
        <input type="password" id="ins_password2" autocomplete="off" name="password2" />

        <label for="ins_email">${_('E-mail')}</label>
        <input type="email" id="ins_email" name="email" autocomplete="off" value="${user.email or ''}" />
        
        <input type="submit" value="${_('Save')}" />
    </form>
</section>

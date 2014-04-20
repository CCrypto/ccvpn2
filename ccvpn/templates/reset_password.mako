<%! title = 'Password Reset' %>
<%inherit file="layout.mako" />

<section id="pwresetpage" class="centeredpage">
    <article>
    <h1>${_('Password Reset')}</h1>
    <form class="vert" action="/account/reset/${token.token}" method="post" class="vertical">
        <label for="ins_password">${_('Password')}</label>
        <input type="password" id="ins_password" name="password" required="required" value="" />
        <label for="ins_password2">${_('Password')} (${_('repeat')})</label>
        <input type="password" id="ins_password2" name="password2" required="required" value="" />

        <input type="submit" value="${_('Reset')}"/>
    </form>
    </article>
    <article class="links">
        <h2>${_('Others Links')}</h2>
        <ul>
            <li><a href="/account/login">${_('You remembered your password? Log in')}</a></li>
            <li><a href="/account/signup">${_('Don\'t have an account? Create one')}</a></li>
            <li><a href="/page/support">${_('Need help?')}</a></li>
        </ul>
    </article>
</section>


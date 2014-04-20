<%! title = 'Log in' %>
<%inherit file="layout.mako" />

<section id="loginpage" class="centeredpage">
    <article>
    <h1>${_('Log in')}</h1>
    <form class="vert" action="/account/login" method="post">
        <label for="ins_username">${_('Username')}</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />

        <label for="ins_password">${_('Password')}</label>
        <input type="password" id="ins_password" name="password" required="required" value="" />

        <input type="submit" value="${_('Log in')}" />
    </form>
    </article>
    <article class="links">
        <h2>${_('Others Links')}</h2>
        <ul>
            <li><a href="/account/signup">${_('Don\'t have an account? Create one')}</a></li>
            <li><a href="/account/forgot">${_('Forgot your password?')}</a></li>
            <li><a href="/page/support">${_('Need help?')}</a></li>
        </ul>
    </article>
</section>


<%! title = 'Sign up' %>
<%inherit file="layout.mako" />

<section id="signuppage" class="centeredpage">
    <article>
    <h1>${_('Sign up')}</h1>
    <form class="vert" action="/account/signup" method="post">
        <label for="ins_username">${_('Username')}</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />
        <p class="inputhelp">${_('2 to 32 alphanumeric characters.')}</p>

        <label for="ins_password">${_('Password')}</label>
        <input type="password" id="ins_password" name="password" required="required" value="${password or ''}" />
        <p class="inputhelp">${_('Anything from 1 to 256 characters. Better choose a strong one.')}</p>

        <label for="ins_password2">${_('Repeat')}</label>
        <input type="password" id="ins_password2" name="password2" required="required" value="${password2 or ''}" />

        <label for="ins_email">${_('E-mail')}</label>
        <input type="email" id="ins_email" name="email" value="${email or ''}" />
        <p class="inputhelp"><b>${_('Optional.')}</b> ${_('Used to recover your password and confirm stuff.')}</p>

        <input type="submit" value="${_('Sign up')}" />
    </form>
    </article>
    <article class="rightsignup links">
        <h2>${_('Others Links')}</h2>
        <ul>
            <li><a href="/account/login">${_('Already a member? Log in')}</a></li>
            <li><a href="/account/forgot">${_('Forgot your password?')}</a></li>
            <li><a href="/page/support">${_('Need help?')}</a></li>
        </ul>
    </article>
    <article class="rightsignup">
        <img src="/static/7proxies.png" style="max-width:90%; margin: 5%" alt="Good luck, I'm behind 7 proxies." />
    </article>
</section>


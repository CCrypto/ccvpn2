<%inherit file="layout.mako" />

<section id="loginpage">
    <article class="login">
    <h1>Log in</h1>
    <form class="vert" action="/account/login" method="post">
        <label for="ins_username">Username</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />

        <label for="ins_password">Password</label>
        <input type="password" id="ins_password" name="password" required="required" value="" />

        <input type="submit" value="Log in" />
    </form>
    </article>
    <article class="linkslogin">
        <h2>Others Links</h2>
        <ul>
            <li><a href="/account/signup">Don't have an account? Create one</a></li>
            <li><a href="/account/forgot">Forgot your password?</a></li>
            <li><a href="/page/support">Need help?</a></li>
        </ul>
    </article>
    <div style="clear: both"></div>
</section>


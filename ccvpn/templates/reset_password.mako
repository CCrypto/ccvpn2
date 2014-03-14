<%! title = 'Password Reset' %>
<%inherit file="layout.mako" />

<section id="pwresetpage" class="centeredpage">
    <article>
    <h1>Password Reset</h1>
    <form class="vert" action="/account/reset/${token.token}" method="post" class="vertical">
        <label for="ins_password">Password</label>
        <input type="password" id="ins_password" name="password" required="required" value="" />
        <label for="ins_password2">Password (repeat)</label>
        <input type="password" id="ins_password2" name="password2" required="required" value="" />

        <input type="submit" />
    </form>
    </article>
    <article class="links">
        <h2>Others Links</h2>
        <ul>
            <li><a href="/account/login">You remembered your password? Log in</a></li>
            <li><a href="/account/signup">Don't have an account? Create one</a></li>
            <li><a href="/page/support">Need help?</a></li>
        </ul>
    </article>
    <div style="clear: both"></div>
</section>


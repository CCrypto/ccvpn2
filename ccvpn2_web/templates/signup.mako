<%inherit file="layout.mako" />

<section>
    <article>
    <h1>Sign up</h1>
    <form action="/account/signup" method="post">
        <label for="ins_username">Username</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />
        <p class="inputhelp">2 to 32 alphanumeric characters.</p>

        <label for="ins_password">Password</label>
        <input type="password" id="ins_password" name="password" required="required" value="${password or ''}" />
        <p class="inputhelp">Anything from 1 to 256 characters. Better choose a strong one.</p>

        <label for="ins_password2">Repeat</label>
        <input type="password" id="ins_password2" name="password2" required="required" value="${password2 or ''}" />

        <label for="ins_email">E-mail:</label>
        <input type="email" id="ins_email" name="email" value="${email or ''}" />
        <p class="inputhelp"><b>Optional.</b> Used to recover your password and confirm stuff.</p>

        <input type="submit" />
    </form>
    </article>
    <div style="clear: both"></div>
</section>


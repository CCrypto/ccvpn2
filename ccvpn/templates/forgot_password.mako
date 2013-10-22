<%inherit file="layout.mako" />

<section>
    <article>
    <h1>Password reset</h1>
    <form action="/account/forgot" method="post" class="vertical">
        <label for="ins_username">Username</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />
        <p class="inputhelp">2 to 32 alphanumeric characters.</p>

        <input type="submit" />
    </form>
    </article>
    <div style="clear: both"></div>
</section>


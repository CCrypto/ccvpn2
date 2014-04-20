<%! title = 'Password Reset' %>
<%inherit file="layout.mako" />

<section id="pwresetpage" class="centeredpage">
    <article>
    <h1>${_('Password Reset')}</h1>
    <form class="vert" action="/account/forgot" method="post">
        <label for="ins_username">${_('Username')}</label>
        <input type="text" id="ins_username" name="username" pattern="[a-zA-Z0-9_-]{2,32}" required="required" value="${username or ''}" />

        <input type="submit" value="${_('Send a reset link')}" />
    </form>
    </article>
</section>


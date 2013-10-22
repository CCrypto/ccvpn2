<%inherit file="../layout.mako" />

<section>
    <h2>User: ${item.username} #${item.id}</h2>
    <article>
        <form action="/admin/user/#${item.id}" method="post">
            <label for="f_id">ID</label>
            <input type="text" name="id" id="f_id" value="${item.id}" />

            <label for="f_username">Username</label>
            <input type="text" name="username" id="f_username" value="${item.username}" />

            <label for="f_password">Password</label>
            <input type="text" name="password" id="f_password" value="${'something' if item.password else 'none'}" />

            <label for="f_email">E-mail</label>
            <input type="text" name="email" id="f_email" value="${item.email}" />

            <label for="f_is_active">Is active?</label>
            <input type="text" name="is_active" id="f_is_active" value="${item.is_active}" />

            <label for="f_is_admin">Is admin?</label>
            <input type="text" name="is_admin" id="f_is_admin" value="${item.is_admin}" />

            <label for="f_signup_date">Signup date</label>
            <input type="text" name="signup_date" id="f_signup_date" value="${item.signup_date}" />

            <label for="f_last_login"></label>
            <input type="text" name="last_login" id="f_last_login" value="${item.last_login}" />

            <label for="f_paid_until">ID</label>
            <input type="text" name="paid_until" id="f_paid_until" value="${item.paid_until}" />
            
            <input type="submit" />
        </form>
    </article>
    <div style="clear: both"></div>
</section>

<%inherit file="layout.mako" />

<section id="account">
    <h2>Account : ${request.user.username}</h2>
    % if request.user.is_paid():
        <article>
            <p>Your account is <b>paid</b> for ${request.user.paid_days_left()} day(s).</p>
        </article>
    % endif

    <article class="two">
        <h3>Settings</h3>
        <form action="/account/" method="post">
            <label for="ins_password">Change password</label>
            <input type="password" id="ins_password" name="password" />

            <label for="ins_password2">Change password (repeat)</label>
            <input type="password" id="ins_password2" name="password2" />

            <label for="ins_email">E-mail</label>
            <input type="email" id="ins_email" name="email" value="${email or ''}" />
            
            <input type="submit" />
        </form>
    </article>
    <article class="two">
        <h3>Renew</h3>
        <form action="/order/" method="post">
            <div class="inlinefield">
            <label for="ino_time">Time</label>
            <select id="ino_time" name="time">
                <option value="1">1 month</option>
                <option value="3">3 months</option>
                <option value="6">6 months</option>
                <option value="12">12 months</option>
            </select>
            </div>
            
            <div class="inlinefield">
            <label for="ino_method">Method</label>
            <select id="ino_method" name="method">
                <option value="paypal">Paypal</option>
                <option value="bitcoin">Bitcoin</option>
            </select>
            </div>

            <div style="clear:both"></div>

            <p>-- or --</p>
            <label for="ins_code">Gift code</label>
            <input type="text" id="ins_code" name="code" pattern="[A-Z0-9]{1,16}" autocomplete="off" />

            <input type="submit" />
        </form>
    </article>
    
    <div style="clear: both"></div>
</section>

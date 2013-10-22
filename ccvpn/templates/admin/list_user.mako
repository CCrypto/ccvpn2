<%inherit file="../layout.mako" />
<%! from ccvpn.models import Base %>
<section>
    <h2><a href="/admin/">Admin</a> - <a href="/admin/${model_name.lower()}s">${model_name}s</a></h2>
    <article>
        <table>
            <tr><td>ID</td>
                <td>Username</td>
                <td>E-Mail</td>
                <td>Active?</td>
                <td>Paid?</td>
                <td>Admin?</td>
                </tr>
            % for item in items:
            <tr><td><a href="/admin/users?id=${item.id}">${item.id}</a></td>
                <td>${item.username}</td>
                <td>${item.email or ''}</td>
                <td>${item.is_active | check}</td>
                <td>${item.is_paid | check}</td>
                <td>${item.is_admin | check}</td>
                </tr>
            % endfor
        </table>
    </article>
    <article>
        <h3>Add</h3>
        <form class="largeform" action="/admin/users" method="post">
                <label for="f_username">Username</label>
                <input type="text" name="username" id="f_username" value="" />
                
                <label for="f_password">Password</label>
                <input type="password" name="password" id="f_password" value="" />
            
                <label for="f_email">E-mail</label>
                <input type="text" name="email" id="f_email" value="" />
            
                <label for="f_is_active">Active?</label>
                <input type="checkbox" name="is_active" id="f_is_active" checked="checked" />
            
                <label for="f_is_admin">Admin?</label>
                <input type="checkbox" name="is_admin" id="f_is_admin"  />
            
                <label for="f_signup_date">Signup date</label>
                <input type="text" name="signup_date" id="f_signup_date" value="2013-08-15 02:40:21.006970" />
            
                <label for="f_last_login">Last login</label>
                <input type="text" name="last_login" id="f_last_login" value="" />
            
                <label for="f_paid_until">Paid until...</label>
                <input type="text" name="paid_until" id="f_paid_until" value="" />
            <input type="submit" value="Add" />
        </form>
    </article>
    <div style="clear: both"></div>
</section>

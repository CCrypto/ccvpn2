<%inherit file="../layout.mako" />

<section>
    <h2>Users</h2>
    <article>
        <table>
            <tr>
                <td>ID</td>
                <td>Username</td>
                <td>E-Mail</td>
                <td>Active?</td>
                <td>Paid?</td>
                <td>Admin?</td>
            </tr>

            % for item in items:
            <tr>
                <td><a href="/admin/user/${item.id}">${item.id}</a></td>
                <td>${item.username}</td>
                <td>${item.email}</td>
                <td>${item.is_active | check}</td>
                <td>${item.is_paid | check}</td>
                <td>${item.is_admin | check}</td>
            </tr>
            % endfor
        </table>
    </article>
    <div style="clear: both"></div>
</section>

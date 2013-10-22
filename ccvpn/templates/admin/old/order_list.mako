<%inherit file="../layout.mako" />

<section>
    <h2>Users</h2>
    <article>
        <table>
            <tr>
                <td>ID</td>
                <td>User</td>
                <td>Paid?</td>
                <td>Amount</td>
                <td>Paid</td>
                <td>Method</td>
            </tr>

            % for item in items:
            <tr>
                <td><a href="/admin/order/${item.id}">${item.id}</a></td>
                <td><a href="/admin/user/${item.user.id}">${item.user.username}</a></td>
                <td>${item.paid | check}</td>
                <td>${item.amount}</td>
                <td>${item.paid_amount}</td>
                <td>${item.method}</td>
            </tr>
            % endfor
        </table>
    </article>
    <div style="clear: both"></div>
</section>

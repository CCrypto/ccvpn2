<%inherit file="../layout.mako" />

<section>
    <h2>Users</h2>
    <article>
        <table>
            <tr>
                <td>ID</td>
                <td>Code</td>
                <td>Time</td>
                <td>Used</td>
            </tr>

            % for item in items:
            <tr>
                <td><a href="/admin/giftcode/${item.id}">${item.id}</a></td>
                <td>${item.code}</td>
                <td>${item.time}</td>
                % if item.used:
                    <td><a href="/admin/user/${item.user.id}">${item.user.username}</a></td>
                % else:
                    <td>No</td>
                % endif
            </tr>
            % endfor
        </table>
    </article>
    <div style="clear: both"></div>
</section>

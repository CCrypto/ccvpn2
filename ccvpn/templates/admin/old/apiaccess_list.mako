<%inherit file="../layout.mako" />

<section>
    <h2>Users</h2>
    <article>
        <table>
            <tr>
                <td>ID</td>
                <td>Label</td>
                <td>Remote</td>
                <td>Expire</td>
            </tr>

            % for item in items:
            <tr>
                <td><a href="/admin/apiaccess/${item.id}">${item.id}</a></td>
                <td>${item.label}</td>
                <td>${item.remote}</td>
                <td>${item.expire}</td>
            </tr>
            % endfor
        </table>
    </article>
    <div style="clear: both"></div>
</section>

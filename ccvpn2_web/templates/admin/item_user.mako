<%inherit file="../layout.mako" />

<section>
    <h2>Admin - ${model_name} - ${str(item)} #${item.id}</h2>
    <article class="two">
        <form action="/admin/${model_name}/${item.id}" method="post">
        % for field in model.edit_fields:
            <%
                doc = getattr(model, field).__doc__
                value = getattr(item, field)
                if value is None:
                    value = ''
            %>
            % if isinstance(value, bool):
                <input type="checkbox" name="${field}" id="f_${field}" checked="${'checked' if value else ''}" />
                <label for="f_${field}">${doc if doc is not None else field}</label>
            % else:
                <label for="f_${field}">${doc if doc is not None else field}</label>
                <input type="text" name="${field}" id="f_${field}" value="${value}" />
            % endif
        % endfor
            <input type="submit" />
        </form>
    </article>
    <article class="two">
        <h3>Orders</h3>
        <table>
            <tr><td>ID</td> <td>Time</td> <td>Paid?</td> <td>Method</td></tr>
            % for order in item.orders:
                <tr>
                    <td><a href="/admin/order/${order.id}">${order.id}</a></td>
                    <td>${order.time}</td>
                    <td>${order.paid | check}</td>
                    <td>${order.method}</td>
                </tr>
            % endfor
        </table>
    </article>
    <article class="two">
        <h3>Gift Codes Used</h3>
        <table>
            <tr><td>ID</td> <td>Code</td> <td>Time</td></tr>
            % for gc in item.giftcodes_used:
                <tr>
                    <td><a href="/admin/giftcode/${gc.id}">${gc.id}</a></td>
                    <td>${gc.code}</td>
                    <td>${gc.time}</td>
                </tr>
            % endfor
        </table>
    </article>
    <div style="clear: both"></div>
</section>

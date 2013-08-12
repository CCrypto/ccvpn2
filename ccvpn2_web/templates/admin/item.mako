<%inherit file="../layout.mako" />

<section>
    <h2>Admin - ${model_name} - ${str(item)} #${item.id}</h2>
    <article>
        <form action="/admin/${model_name.lower()}s?id=${item.id}" method="post">
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
    <div style="clear: both"></div>
</section>

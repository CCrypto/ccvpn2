% if item_title:
    <h3>${item_title}</h3>
% endif

<form class="largeform" action="" method="post">
% for field in view_context.edit_fields:
    <%
        value = getattr(item, field.attr)
        if value is None:
            value = ''
    %>
    <label for="f_${field}">${field.name}</label>
    <input
        name="${field.id}"
        id="f_${field.id}"
        % if not field.writable:
            disabled="disabled"
        % endif
        % if isinstance(value, bool):
            type="checkbox"
            % if value:
                checked="checked"
            % endif
        % else:
            value="${value}"
        % endif
    />
% endfor
    <input type="submit" value="Save" />
</form>

<h3>Add ${view_context.without_id().title}</h3>

<form class="largeform" action="" method="post">
% for field in view_context.edit_fields:
    <%
        if field.editonly:
            continue
    %>
    <label for="f_${field.id}">${field.name}</label>
    <input
        name="${field.id}"
        id="f_${field.id}"
        % if isinstance(field.default, bool):
            type="checkbox"
            % if field.default:
                checked="checked"
            % endif
        % else:
            type="text"
            value="${field.default}"
        % endif
    />
% endfor
    <input type="submit" value="Save" />
</form>

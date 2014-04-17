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
    <label for="f_${field.id}">${field.name}</label>
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
            type="text"
            % if field.placeholder:
                value=""
                placeholder \
            % else:
                value \
            % endif
            ="${field.ofilter(value)}"
        % endif
    />
% endfor
% if view_context.can_edit:
    <input type="submit" value="Save" />
% endif
</form>

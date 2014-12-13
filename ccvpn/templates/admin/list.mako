<form class="inline" method="get" action="">
    <input type="text" name="search" />
    <input type="submit" value="Search" />
</form>

<table class="admin-list">
<thead>
    <tr>
    % for field in view_context.list_fields:
        <td>${field.name}</td>
    % endfor
    </tr>
</thead>
<tbody>
    % for item in list_items:
    <tr>
        % for field in view_context.list_fields:
            <% value = getattr(item, field.attr) %>

            <td>
            % if field.link:
                <a href="${field.link.format(**vars(item))}">
            % endif

            % if value is True:
                &#x2611;
            % elif value is False:
                &#x2612;
            % elif value is not None:
                ${field.filter(value)}
            % endif

            % if field.link:
                </a>
            % endif
            </td>
        % endfor
    </tr>
    % endfor
</tbody>
</table>
<p class="pages">
    % if page > 0:
        <a href="?page=0">&lt;&lt;</a>
        <a href="?page=${page - 1}">&lt;</a>
    % endif
    <a href="?page=${page}">${page}</a>
    % if page < pages - 1:
        <a href="?page=${page + 1}">&gt;</a>
        <a href="?page=${pages - 1}">&gt;&gt;</a>
    % endif
</p>


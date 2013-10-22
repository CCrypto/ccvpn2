<%inherit file="../layout.mako" />
<%! from ccvpn.models import Base %>
<section>
    <h2><a href="/admin/">Admin</a> - <a href="/admin/${model_name.lower()}s">${model_name}s</a></h2>
    <article>
        <table>
            <tr>
            % for field in model.list_fields:
                <td>
                % if getattr(model, field).__doc__ is not None:
                    ${getattr(model, field).__doc__}
                % else:
                    ${field}
                % endif
                </td>
            % endfor
            </tr>

            % for item in items:
            <tr>
                % for field in model.list_fields:
                    <%
                        modelfield = getattr(model, field)
                        attr = getattr(item, field)
                        before = ''
                        after = ''
                        if hasattr(modelfield, 'primary_key') and modelfield.primary_key:
                            before += '<a href="/admin/%ss?id=%s">'%(model_name.lower(), attr)
                            after += '</a>'
                        elif isinstance(attr, Base):
                            name = attr.__class__.__name__.split('.')[-1].lower()
                            before += '<a href="/admin/%ss?id=%s">'%(name, attr.id)
                            after += '</a>'
                    %>
                    <td>
                    ${before|n}
                    % if isinstance(attr, bool):
                        ${'&#x2611;' if attr else '&#x2612;' | n}
                    % else:
                        ${attr}
                    % endif
                    ${after|n}
                    </td>
                % endfor
            </tr>
            % endfor
        </table>
    </article>
    <article>
        <h3>Add</h3>
        <form class="largeform" action="/admin/${model_name.lower()}s" method="post">
        % for field in model.edit_fields:
            <%
                doc = getattr(model, field).__doc__
                value = ''
                if hasattr(getattr(model, field), 'default'):
                    default = getattr(model, field).default
                    if hasattr(default, 'arg'):
                        value = default.arg
                        if hasattr(value, '__call__'):
                            value = value(None) # Why None ? I have no idea.
            %>
            % if isinstance(value, bool):
                <label for="f_${field}">${doc if doc is not None else field}</label>
                <input type="checkbox" name="${field}" id="f_${field}" ${'checked="checked"' if value else '' | n} />
            % else:
                <label for="f_${field}">${doc if doc is not None else field}</label>
                <input type="text" name="${field}" id="f_${field}" value="${value}" />
            % endif
        % endfor
            <input type="submit" value="Add" />
        </form>
    </article>
    <div style="clear: both"></div>
</section>

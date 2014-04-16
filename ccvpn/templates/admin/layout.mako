<%inherit file="../layout.mako" />
<section>
    <div class="left_menu">
        <p class="title"><a href="/admin/">Admin</a></p>
        <ul>
            % for lmi in left_menu:
                % if lmi is None:
                    <li class="separator"></li>
                % else:
                    <li><a href="${lmi[0]}">${lmi[1]}</a></li>
                % endif
            % endfor
        </ul>
    </div>
    <article>
        <h2>
            % for ctx in view_context.context_rev():
                <% ctxr = ctx.without_id() %>
                :: <a href="${request.resource_url(ctxr)}">${ctxr.title}</a>
                % if ctx.id:
                    :: <a href="${request.resource_url(ctx)}">${ctx.title}</a>
                % endif
            % endfor
        </h2>
    % for template in templates:
            <%include file="${template}" />
    % endfor
    </article>
</section>


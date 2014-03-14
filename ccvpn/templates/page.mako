<%inherit file="layout.mako" />

<section>
    <article>
        % if title:
            <h1>${title}</h1>
        % endif
        ${content | n}
    </article>
</section>


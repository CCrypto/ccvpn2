<%! title = 'New Ticket' %>
<%inherit file="../layout.mako" />

<section class="centeredpage">
<article>
    <h1>${_('New Ticket')}</h1>

    <form class="vert" action="" method="post">
        <label for="in_subject">${_('Subject')}</label>
        <input type="text" id="in_subject" name="subject" required="required" value="${subject or ''}" />

        <label for="in_message">${_('Message')}</label>
        <textarea id="in_message" name="message" required="required">${message or ''}</textarea>

        <input type="submit" value="${_('Open Ticket')}" />
    </form>
</article>
</section>


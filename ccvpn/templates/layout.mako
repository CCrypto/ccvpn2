<%!
    title_ = None
%>
<%
    menuItems = [
        ['Home', '/'],
        ['Help', '/page/help'],
        ['Servers', '/gateways'],
    ]
    if request.user and request.user.is_admin:
        menuItems.append(['Admin', '/admin/'])
    path = request.path
    for k in menuItems:
        if path == k[1] or (k[1] != '/' and k[1][-1] == '/' and path.startswith(k[1])):
            k.append(' class=\"selected\"')
        else:
            k.append('')
    
    settings = request.registry.settings
    use_https = settings.get('use_https', False)
    if use_https:
        ssl_port = settings.get('https_port', 443)
        ssl_url = request.current_route_url(_scheme='https', _port=ssl_port)

    if title:
        title_pre = title + ' - '
    elif hasattr(self.attr, 'title') and self.attr.title:
        title_pre = self.attr.title + ' - '
    else:
        title_pre = ''

%>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>${title_pre}CCrypto VPN</title>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="/static/reset.css" media="screen" />
    <link rel="stylesheet" href="/static/style.css" media="screen" />
</head>
<body>
    <div id="topbar">
        <div class="topbar-left">
            <p>
                <a href="http://ccrypto.org">Cognitive Cryptography</a>
                % if use_https and request.host_port != str(ssl_port):
                    // <a href="${ssl_url}"><b>Secure version</b></a>
                % endif
            </p>
        </div>
        <div class="topbar-right">
            % if request.user:
                <p><a class="create" href="/account/">Your account</a>
                    <a class="create" href="/account/logout">Logout</a>
                    </p>
            % else:
                <p><a href="/account/signup" class="create">Sign up</a>
                    <a href="/account/login" class="create">Log in</a>
                    </p>
            % endif
        </div>
        <div style="clear:both"></div>
    </div>
    
    <header>
        <div id="logo">
            <h2><a href="//ccrypto.org/">CCrypto</a></h2>
            <h1><a href="/">VPN</a></h1>
        </div>
        <nav>
            <ul>
                % for menuItem in menuItems:
                    <li${menuItem[2] | n}><a href="${menuItem[1]}">${menuItem[0]}</a></li>
                % endfor
            </ul>
        </nav>
        <div style="clear: both"></div>
    </header>

    <div class="wrap">
        % for packed in request.session.pop_flash():
        <% t, m = packed if len(packed) == 2 else ('info', packed) %>
        <div class="message">
            <p class="${t}">${m}</p>
        </div>
        % endfor
    
        ${self.body()}
    </div>

    <footer>
        <p>Copyleft 2013 <a href="//ccrypto.org/">Cognitive Cryptography</a>
        - <a href="/page/tos">ToS</a>
        - <a href="/page/support">Abuse report</a>
        - <a href="https://github.com/CCrypto/ccvpn">It's open-source!</a>
        </p>
    </footer>
</body>
</html>


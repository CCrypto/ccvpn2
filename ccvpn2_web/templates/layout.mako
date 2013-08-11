<%
    menuItems = [
        ['Home', '/'],
        ['Docs', '/page/docs'],
        ['FAQ', '/page/faq'],
        ['Support', '/page/support'],
    ]
    if request.user and request.user.is_admin:
        menuItems.append(['Admin', '/admin/'])
    path = request.path
    for k in menuItems:
        if path == k[1] or (k[1] != '/' and k[1][-1] == '/' and path.startswith(k[1])):
            k.append(' class=\"selected\"')
        else:
            k.append('')
%>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>CCrypto VPN</title>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="/static/reset.css" media="screen" />
    <link rel="stylesheet" href="/static/style.css" media="screen" />
</head>
<body>
    <div id="topbar">
        % if request.user:
            <p>
                <a class="create" href="/account/">Your account</a>
                <a class="create" href="/account/logout">Logout</a>
            </p>
        % else:
        <form action="/account/login" method="post">
            <a href="/account/signup" class="create">Sign up</a>
            <a href="/account/forgot" class="login-helper">Forgot password?</a>
            <input id="in_username" type="text" name="username" placeholder="Username"></input>
            <input id="in_password" type="password" name="password" placeholder="Password"></input>
            <input value="Login" type="submit">
        </form>
        % endif
    </div>
    
    <header>
        <div id="title">
            <h1><a href="/">VPN</a></h1>
            <h2><a href="//ccrypto.org/">By CCrypto</a></h2>
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

        % for packed in request.session.pop_flash():
        <% t, m = packed if len(packed) == 2 else ('info', packed) %>
        <article class="message">
            <p class="${t}">${m}</p>
        </article>
        % endfor
    
    ${self.body()}
    
    <footer>
        <p>Copyleft 2013 <a href="//ccrypto.org/">Cognitive Cryptography</a> - <a href="/page/tos">ToS</a> - <a href="/page/support">Abuse report</a></p>
    </footer>
</body>
</html>


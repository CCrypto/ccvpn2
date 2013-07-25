<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>CCrypto VPN</title>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="/static/style.css" media="screen" />
    <link rel="stylesheet" href="/static/style-tty.css" media="tty" />
</head>
<body>
    <div id="topbar">
        <form action="/account/login" method="post">
            <a href="/account/signup" class="create">Sign up</a>
            <a href="/account/forgot" class="login-helper">Forgot password?</a>
            <input id="in_username" type="text" name="username" placeholder="Username"></input>
            <input id="in_password" type="password" name="password" placeholder="Password"></input>
            <input value="Login" type="submit">
        </form>
    </div>
    
    <header>
        <div id="title">
            <h1><a href="/">VPN</a></h1>
            <h2><a href="//ccrypto.org/">By CCrypto</a></h2>
        </div>

        <nav>
            <ul>
                <li class="selected"><a href="/">Home</a></li>
                <li><a href="/">Docs</a></li>
                <li><a href="/">FAQ</a></li>
                <li><a href="/">Support</a></li>
            </ul>
        </nav>

        <div style="clear: both"></div>
    </header>
    
    ${self.body()}
    
    <footer>
        <p>Copyleft 2013 <a href="//ccrypto.org/">Cognitive Cryptography</a> - <a href="/">CGU</a> - <a href="/">Abuse report</a></p>
    </footer>
</body>
</html>


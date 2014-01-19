Save password in config
=======================

If you don't want to type your username/password every time, you can save
it in a text file somewhere, like in your OpenVPN directory,
and put your username and password in it on two lines:

    JackSparrow
    s0mep4ssw0rd


Now open your OpenVPN config file (.conf/.ovpn) as any text file and link the
previous file with auth-user-pass using its full path:

    [...]
    auth-user-pass /etc/openvpn/openvpn-creds.txt

If you run a UNIX-like OS, you can deny every user except root to read it:

    chown root:root /etc/openvpn/openvpn-creds.txt
    chmod 600 /etc/openvpn/openvpn-creds.txt


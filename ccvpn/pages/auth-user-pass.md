Save password in config
-----------------------

Create a text file somewhere, like in your OpenVPN directory,
and put your username and password in it on two lines:

    JackSparrow
    s0mep4ssw0rd


Now open your OpenVPN config file (.conf/.ovpn) and link the previous file
with auth-user-pass:

    [...]
    auth-user-pass /etc/openvpn/openvpn-creds.txt

If you run a UNIX-like OS, you can deny every user except root to read it:

    chown root:root /etc/openvpn/openvpn-creds.txt
    chmod 600 /etc/openvpn/openvpn-creds.txt


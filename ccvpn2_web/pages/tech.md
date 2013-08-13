Tech Stuff
==========

Software
--------
We use OpenVPN on GNU/Linux, with tun.
Every port is allowed, on TCP an UDP, with IPv4 and IPv6.

You can connect to OpenVPN servers with:

  - "Alpha" : UDP, default port. Default, recommended.
  - "Beta" : TCP, port 443 (HTTPS). It should pass through most of the firewalls, but it is slower and less reliable than Alpha.  
    Use it only if Alpha does NOT work for you.

Security
--------
We have a 4096b RSA key for authentication and key exchange,
and allow the best ciphers available to provide *perfect forward secrecy*
to up-to-date clients.

Client certificate authentication
---------------------------------
We allow you to authenticate with a certificate instead of a password.  
This is not available in the user panel through ;
you will need to send us a certificate signing request by email to
the support and we will send you back the signed certificate.

IPv4 ports forwarding
---------------------
Because of the cost of IPv4 adresses,
you share your IPv4 address behind a NAT router,
but you can ask to have a port range forwarded.

IPv6
----
All of our gateways support IPv6.
Each connected client is provided his own a IPv6 address
with all ports open for TCP and UDP.




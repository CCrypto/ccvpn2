Install on GNU/Linux
====================

You will need a config file : In [your account](/account/), download the
.ovpn file. You can rename it to .conf.

**Do not use Network-Manager. It is known to not work.**  
N-M ignores some of OpenVPN's config options, and simply cannot connect to
our VPN.  
We are still waiting for this issue to be fixed.

If you have any questions, go to the [Support page](/page/support).

Debian/Ubuntu
-------------
Login as root.  
Put the config file you have downloaded in `/etc/openvpn/`.  
ie: `/etc/openvpn/ccrypto.conf`

Now, you can start it :

    service openvpn start ccrypto

To start it on boot, edit `/etc/default/openvpn` and uncomment/change the `AUTOSTART` line:

    AUTOSTART="ccrypto"

Other
-----

You should check for a distribution-specific install howto :

* <a href="https://wiki.archlinux.org/index.php/OpenVPN">ArchLinux</a>


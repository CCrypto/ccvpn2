Install on GNU/Linux
--------------------

You should check for a distribution-specific install howto :

* <a href="https://wiki.archlinux.org/index.php/OpenVPN">ArchLinux</a>
* <a href="https://help.ubuntu.com/community/OpenVPN">Ubuntu</a>
* <a href="http://doc.ubuntu-fr.org/openvpn">Ubuntu (FR)</a>
* <a href="http://wiki.debian.org/OpenVPN">Debian</a>

You will need a config file : In [your account](/account/), download the config file. It should be a .ovpn file, and you may need to rename it to *.conf.

If you have any questions, go to the Support page.

Debian/Ubuntu
-------------
Login as root.  
Put the config file you have downloaded in `/etc/openvpn/`, ie: `/etc/openvpn/ccrypto-alpha.conf`  

Now, you can start it :

    service openvpn start ccrypto-alpha

To start it on boot, edit `/etc/default/openvpn` and uncomment/change the `AUTOSTART` line:

    AUTOSTART="ccrypto-alpha"



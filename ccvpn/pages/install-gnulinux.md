Title: Install on GNU/Linux

You will need a config file : In [your account](/account/), download the
.ovpn file. You can rename it to .conf.

**Do not use Network-Manager. It is known to not work.**  
N-M ignores some of OpenVPN's config options, and simply cannot connect to
our VPN.  
We are still waiting for this issue to be fixed.

If you have any questions, go to the [Support page](/page/help).


Fedora 16 or later
------------------
**You need to login as root for all these commands, or use sudo.**  

    yum install openvpn

Put the config file you have downloaded in `/etc/openvpn/`.  
ie: `/etc/openvpn/ccrypto.conf`

    cd /lib/systemd/system
    ln openvpn@.service openvpn@ccrypto.service

Start it:

    systemctl start openvpn@ccrypto.service

Now, you can make it start on boot. It should ask for your password on boot.
You can start it on boot:

    systemctl enable openvpn@ccrypto.service


Debian/Ubuntu
-------------
**You need to login as root for all these commands, or use sudo.**  

Download and install OpenVPN:

    apt-get install openvpn resolvconf

Put the config file you have downloaded in `/etc/openvpn/`.  
ie: `/etc/openvpn/ccrypto.conf`

Now, you can start it :

    service openvpn start ccrypto

To start it on boot, [save your creditentials](/page/auth-user-pass) first, and
edit `/etc/default/openvpn` and uncomment/change the `AUTOSTART` line:

    AUTOSTART="ccrypto"


Linux Mint 17 Mate Edition or later
-------------

First, you have to update your system by using the following command:

```
sudo aptitude update
```

Download and install OpenVPN and Network-manager-openvpn-gnome:

```
sudo aptitude install openvpn resolvconf network-manager-openvpn-gnome
```

Reboot your system .

Save the config file [you've downloaded from your ccrypto account section](https://vpn.ccrypto.org/account/) into /etc/openvpn/.
Rename the file to eg. ccrypto-*.conf if necessary.

[Download the ca.crt file](https://vpn.ccrypto.org/ca.crt) and put it in /etc/opvpn aswell.

- Left click on the Network icon in the Control Panel> Network Connections> Add
- Select "Import a saved VPN configuration"
- Select your ccrypto-*.conf config file from the /etc.openvpn directory

Select "password authentication"  as the authentication type and enter your ccrypto username and password.
Select the ca.crt you saved into /etc/openvpn and click "Save".

Your VPN is now ready to use.

Save username and password
--------------------------
You can make OpenVPN remember your username and password, so you don't need
to type them everytime you want to use the VPN.  

This can be done by creating a text file named "ccrypto_creds.txt" containing
your username on the first line and your password on the second
(see example below).  
Put it in /etc/openvpn/, along with the config file.  

It should look like this:

    JackSparrow
    s0mep4ssw0rd

Then, open the .ovpn or .conf file with a text editor (vim, gedit, kate, ...)
and add this line at the end of the file:

    auth-user-pass /etc/openvpn/ccrypto_creds.txt

Now, if you restart OpenVPN, it should not ask you for your password anymore.

You can make sure only root will be able to access this file:

    chown root:root /etc/openvpn/ccrypto_creds.txt
    chmod 600 /etc/openvpn/ccrypto_creds.txt


Other
-----

You should check for a distribution-specific install howto :

* <a href="https://wiki.archlinux.org/index.php/OpenVPN">ArchLinux</a>


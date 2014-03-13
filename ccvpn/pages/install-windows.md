Install on Windows
==================

First, you need to download OpenVPN:
[OpenVPN.net](http://openvpn.net/index.php/open-source/downloads.html)  
Get the `Windows Installer` and install OpenVPN.

In [your account](/account/), download the config file (.ovpn) you want to use,
and copy it to `C:\Program Files\OpenVPN\config\`.

To start using it, run `OpenVPN GUI` you just installed **as Administrator**.  
In the Windows System Tray, you should see a OpenVPN icon;  
right click on it, and click on `Connect`.  

If you have any questions, go to the [Support page](/page/support).  


Save username and password
--------------------------
You can make OpenVPN remember your username and password, so you don't need
to type them everytime you want to use the VPN.  

This can be done by creating a text file named "ccrypto_creds.txt" containing
your username on the first line and your password on the second
(see example below).  
Move it to `C:\Program Files\OpenVPN\config\`, next to the .ovpn file you
copied there before.  

It should look like this:

    JackSparrow
    s0mep4ssw0rd

Then, open the .ovpn file with a text editor (Notepad, Notepad++, ...)
and add this line at the end of the file:

    auth-user-pass ccrypto_creds.txt

Now, if you restart OpenVPN, it should not ask you for your password anymore.


netsh.exe error
---------------

    NETSH: C:\Windows\system32\netsh.exe interface ipv6 set address Connexion au réseau local
    ERROR: netsh command failed: returned error code 1

This error is really frequent on Windows and seem to happen because of
a OpenVPN problem with netsh.exe and IPv6.  
To fix it, rename your network connection to avoid spaces,
for example "Connexion au réseau local" to "local".

  - [(fr) Renommer une connexion réseau](http://windows.microsoft.com/fr-xf/windows-vista/rename-a-network-connection)
  - [(en) Rename a network connection](http://windows.microsoft.com/en-au/windows-vista/rename-a-network-connection)


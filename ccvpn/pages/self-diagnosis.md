Title: Self Diagnosis

I have a ".ovpn" file but I need a ".conf"!
--------
You just have to change the suffix by renamming the file.

I'm unable to use your VPN with Network-Manager.
--------
First, check that you have properly created the profile (tutorial to come).  
If it's the case, before anything else, let's make sure that OpenVPN itself is working with the following command:  
`sudo openvpn --config ccrypto.conf`  
(make sure to replace "ccrypto.conf" by the actual name of your configuration file)

I'm connected but cannot ping google.com o_o
--------
Try to `ping 8.8.8.8`, if it works then your computer doesn't use the right DNS server. Add `nameserver 10.99.0.20` at the beginning of /etc/resolv.conf **once the connection is made**. Else, continue reading.

It still doesn't work!
--------
Using the `ip r` (short for `ip route`) command, make sure you have, alongside with other lines, the following:  
> `0.0.0.0/1 via 10.99.2.1 dev tun0`  
> `10.99.0.0/24 via 10.99.2.1 dev tun0`  
> `10.99.2.0/24 dev tun0  proto kernel  scope link  src 10.99.2.18`  
> `128.0.0.0/1 via 10.99.2.1 dev tun0`  
> `199.115.114.65 via 192.168.1.1 dev wlan0`  
These values might (and for some, will) change a little depending on your configuration (for example: wlan0 → eth0, 192.168.1.1 → 192.168.42.23, etc.).  
If you don't have every one of these lines, kill OpenVPN and fire it again or add the routes by hand using `ip r a` (`ip route add`). If you don't know how to do it, it would be best to come ask on IRC (we will need the output of both `ip a` (`ip address`) and `ip r`, please paste them into https://paste.cubox.me and just give us the link to the paste).

I've tried everything but nothing seems to work! T_T
---------
Ok… I guess now you can come [ask us on IRC](https://kiwiirc.com/client/chat.freenode.net/?nick=ccvpn|?&theme=cli#ccrypto) (but remember to stay a while, we're not payed professionnal, we might not be around at a given time but we will answer later on).


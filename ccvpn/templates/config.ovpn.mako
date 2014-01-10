# +---------------------------+
# |Cognitive Cryptography  VPN|
# |  http://vpn.ccrypto.org/  |
# +---------------------------+
# ${username}${'/'+profile.name if profile else ' (default profile)'}

verb 4
client
tls-client
remote-cert-tls server
dev tun0
tun-ipv6

auth-user-pass
# you can use this and put username/password, one per line, in a file
# auth-user-pass cred.txt

## de.blinkt.openvpn does not support <connection>, so we only use TCP.
% if not android:
remote ${gateway} 1194 udp
% endif
remote ${gateway} 443 tcp

resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo
dhcp-option DNS 10.99.0.20

# Change default routes
redirect-gateway def1
route-ipv6 2000::/3 

# Force Windows to apply new DNS settings
register-dns

<ca>
${openvpn_ca}</ca>


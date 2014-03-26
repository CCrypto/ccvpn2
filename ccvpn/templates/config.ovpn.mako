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

% if force_tcp:
remote ${gateway} 443 tcp
% else:
<connection>
remote ${gateway} 1194 udp
remote ${gateway} 443 tcp
</connection>
% endif

resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo
dhcp-option DNS 10.99.0.20

# Change default routes
redirect-gateway def1
route-ipv6 2000::/3 

% if windows_dns:
# Force Windows to apply new DNS settings
#register-dns
% endif

% if resolvconf:
# Update DNS with resolvconf
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
% endif

<ca>
${openvpn_ca}</ca>


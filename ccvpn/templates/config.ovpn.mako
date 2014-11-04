# +---------------------------+
# |Cognitive Cryptography  VPN|
# |  http://vpn.ccrypto.org/  |
# +---------------------------+
# ${username}${'/'+profile.name if profile.name else ' (default profile)'}

verb 4
client
tls-client
script-security 2
remote-cert-tls server
dev tun

auth-user-pass
# you can use this and put username/password, one per line, in a file
# auth-user-pass cred.txt

remote-random-hostname
server-poll-timeout 4
mssfix 1300

% if force_tcp:
remote ${gateway} 443 tcp
% else:
remote ${gateway} 1194 udp
fragment 1300
% endif

resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo

% if dhcp:
dhcp-option DNS 10.99.0.20
% endif

# Change default routes
redirect-gateway def1

% if ipv6:
tun-ipv6
route-ipv6 2000::/3 
%endif

% if windows_dns:
# Force Windows to apply new DNS settings
#register-dns
% endif

% if resolvconf:
# Update DNS with resolvconf
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
% endif

% if force_tcp and http_proxy:
http-proxy ${http_proxy}
%endif


<ca>
${openvpn_ca}</ca>


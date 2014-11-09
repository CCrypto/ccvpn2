# +---------------------------+
# |Cognitive Cryptography  VPN|
# |  http://vpn.ccrypto.org/  |
# +---------------------------+
# ${profile.vpn_username}

verb 4
client
tls-client
script-security 2
remote-cert-tls server
dev tun
resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo yes
remote-random-hostname
server-poll-timeout 4
auth-user-pass

remote ${remote}

% if use_fragment:
fragment 1300
mssfix 1300
% endif

% if use_http_proxy and profile.use_http_proxy:
http-proxy ${profile.use_http_proxy}
% endif

# Change default routes
redirect-gateway def1

% if use_ipv6:
# Enable IPv6
tun-ipv6
route-ipv6 2000::/3 
%endif

% if use_resolvconf:
# Update DNS with resolvconf
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
% endif


<ca>
${openvpn_ca}</ca>


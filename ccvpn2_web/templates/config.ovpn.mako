# Cognitive Cryptography VPN
# ${username}${'/'+profile.name if profile else ' (default profile)'}

verb 3
client
tls-client
dev tun0
tun-ipv6

auth-user-pass
# you can use this and put username/password, one per line, in a file
# auth-user-pass cred.txt

% if udp:
proto udp
port 1194
% else:
proto tcp
port 443
% endif

% for remote in remotes:
remote ${remote}
% endfor

resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo
redirect-gateway def1

<ca>
${ca_content}</ca>


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

<connection>
% for remote in remotes:
remote ${remote} 1194 udp
% endfor
</connection>

<connection>
% for remote in remotes:
remote ${remote} 443 tcp
% endfor
</connection>

resolv-retry infinite
nobind
persist-key
persist-tun
comp-lzo
redirect-gateway def1

<ca>
${ca_content}</ca>


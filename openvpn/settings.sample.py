
# API base URL
api_baseurl = http://vpn.ccrypto.org/api/server

# API token
api_token = 

# OpenVPN client status directory
status_dir = /dev/shm/ccvpn-status/

# OpenVPN log directory
log_dir = /var/log/openvpn

# Enable IPv6
ipv6_enable = True

# IPv6 _ /64 _ external address (a:b:c:d)
ipv6_addr = 0:1:2:3

# User/group allowed to use management interface
management_user = 'vpnadmin'
management_group = 'vpnadmin'

# Management socket path (PREFIX + PROFILE + ".sock")
management_prefix = '/run/openvpn_'

# Port to share (None to disable)
port_share = None
port_share_host = '127.0.0.1'


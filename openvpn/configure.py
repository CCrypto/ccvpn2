#!/usr/bin/env python
import os

cvars = [
    # name, display name, default value
    ('api_baseurl', 'API base URL', 'http://vpn.ccrypto.org/api/server'),
    ('api_token', 'API token', ''),
    ('status_dir', 'OpenVPN client status directory', '/dev/shm/ccvpn-status/'),
    ('log_dir', 'OpenVPN log directory', '/var/log/openvpn'),
    ('ipv6_enable', 'Enable IPv6', True),
    ('ipv6_addr', 'IPv6 _ /64 _ external address (a:b:c:d)', '0:1:2:3'),
]

try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass


def main():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    output = ''
    settings_file = './settings.py'
    
    try:
        import settings
        settings = {item:getattr(settings, item) for item in dir(settings) if not item.startswith("__")}
    except:
        settings = {v[0]:v[2] for v in cvars}

    for v in cvars:
        print('')
        default = settings[v[0]] if v[0] in settings else v[2]
        value = input('%s ? [%s] '%(v[1], default))
        output += '%s = %s\n'%(v[0], repr(value or default))
    
    with open(settings_file, 'w') as f:
        f.write(output)
    print('Saved to '+settings_file)

def make_empty():
    settings_file = './settings.sample.py'
    output = ''
    for v in cvars:
        output += '\n# %s\n' % v[1]
        output += '%s = %s\n' % (v[0], v[2])
    
    with open(settings_file, 'w') as f:
        f.write(output)
    print('Saved to '+settings_file)

if __name__ == '__main__':
    main()


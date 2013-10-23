#!/usr/bin/python
import sys
import requests
import os
from subprocess import call
from settings import api_baseurl, api_token

api_url = api_baseurl+"/config"

if len(sys.argv) < 2:
    print "not enought args"
    exit(1)

#trusted_ip = os.environ["trusted_ip"]

headers = {
    'X-API-Token' : api_token,
}
data = {
    'username' : os.environ["common_name"],
}

r = requests.get(api_url, headers=headers, params=data)

if r.status_code == 200:
    if len(r.content) != 0:
        config = open(sys.argv[1], "w")
        config.write(r.content)
        config.close()
    if 'trusted_ip6' in os.environ:
        ipv6 = os.environ['trusted_ip6']
        cmd = 'ip -6 neigh add proxy '+ipv6+' dev eth0'
        call(cmd, shell=True)
    exit(0)
else:
    exit(1)


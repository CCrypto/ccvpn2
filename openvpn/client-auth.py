#!/usr/bin/env python
import sys
import requests
from settings import api_baseurl, api_token

api_url = api_baseurl+"/auth"

if len(sys.argv) < 2:
    print "not enought args"
    exit(1)

creds = open(sys.argv[1], 'r')
lines = [line.strip() for line in creds]

headers = {
    'X-API-Token' : api_token,
}
data = {
    'username' : lines[0],
    'password' : lines[1],
}

r = requests.post(api_url, headers=headers, data=data)

if r.status_code == 200:
    exit(0)
else:
    exit(1)


#!/usr/bin/python
import sys
import requests
import os
from settings import api_baseurl, api_token

api_url = api_baseurl+"/disconnect"

headers = {
    'X-API-Token' : api_token,
}
data = {
    'username' : os.environ["common_name"],
}

r = requests.post(api_url, headers=headers, data=data)

exit(0)


#!/usr/bin/env python
from mako.template import Template
from mako import exceptions
import os

profiles = ('alpha', 'beta')

try:
    import settings
    settings = {item:getattr(settings, item) for item in dir(settings) if not item.startswith("__")}
except:
    print('Cannot import settings!')
    exit(1)

settings['root'], _ = os.path.split(os.path.abspath(__file__))

common_tpl = Template(filename='./templates/common.conf')

if not os.path.exists('./config/'):
    os.mkdir('./config/')

for profile in profiles:
    profile_tpl = Template(filename='./templates/profile_%s.conf'%profile)
    filename = './config/%s.conf'%profile
    with open(filename, 'w') as f:
        try:
            common_c = common_tpl.render(**settings)
            profile_c = profile_tpl.render(**settings)
        except:
            print(exceptions.text_error_template().render())
            exit(1)
        f.write(common_c)
        f.write(profile_c)
    print('[+] '+filename)


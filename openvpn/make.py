#!/usr/bin/env python
from mako.template import Template
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
    filename = './config/%s.conf'%profile
    f = open(filename, 'w')
    f.write(common_tpl.render(**settings))
    f.write(Template(filename='./templates/profile_%s.conf'%profile).render(**settings))
    f.close()
    print('[+] '+filename)


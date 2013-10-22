CCrypto VPN 
===========

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_ccvpn_db development.ini

- $venv/bin/pserve development.ini


Bitcoin Payments
----------------

You will need to run a script regularly to check for verified transaction.
With this app installed in /home/vpn/ccvpn/, add this in your crontab:

    */5 * * * * /home/vpn/ccvpn/cron_checkbtcorders.sh /home/vpn/ccvpn/development.ini


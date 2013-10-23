CCrypto VPN 
===========

Getting Started
---------------

It only works with PostgreSQL for now, because of the INET type.

```bash
    git clone https://github.com/CCrypto/ccvpn.git
    cd ccvpn/

    # Use --user if you're not root
    ./setup.py develop
    
    # Prepare the database
    initialize_ccvpn_db development.ini
    
    # Run the dev web server
    pserve development.ini
```

The default "admin" account has the password "admin".

OpenVPN
-------

```bash
    # Generate a secret token for your OpenVPN server
    ccvpn_apiacl ./development.ini add localhost

    cd openvpn/
    
    # You can copy and customize settings.py, or use this script:
    ./configure.py
    
    # run make.py. it renders config files to config/ for each profile
    ./make.py

    # On a standard GNU/Linux distribution, OpenVPN config files are stored in
    # /etc/openvpn. Copy them or make links:
    ln -s $(pwd)/config/alpha.conf /etc/openvpn/ccvpn-alpha.conf
    ln -s $(pwd)/config/beta.conf /etc/openvpn/ccvpn-beta.conf

    # On Debian/Ubuntu:
    service openvpn start ccvpn-alpha
    service openvpn start ccvpn-beta
```

Bitcoin Payments
----------------

You will need to run a script regularly to check for verified transaction.
With this app installed in /home/vpn/ccvpn/, add this in your crontab:

    */5 * * * * /home/vpn/ccvpn/cron_checkbtcorders.sh /home/vpn/ccvpn/development.ini


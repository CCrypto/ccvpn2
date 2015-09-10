Title: Installation sous GNU/Linux

Vous aurez besoin d'un fichier : Dans [votre compte](/account/), téléchargez
la config. Vous pouvez le renommer en ccrypto.conf.

**N'utilisez pas le plugin OpenVPN pour Network-Manager.**  
N-M ne supporte pas certaines options récentes d'OpenVPN, et ne peut simplement
pas se connecter à notre VPN.

Si vous avez une question, n'hésitez pas à [nous contacter](/page/help).


Fedora 16 ou plus récent
------------------------
**Vous devez être connecté en tant que root pour démarrer le VPN.
Il est aussi possible d'utiliser sudo.**  

Installez OpenVPN :

    yum install openvpn

Placez le fichier que vous avez téléchargé dans `/etc/openvpn/`.  
Par exemple : `/etc/openvpn/ccrypto.conf`

    cd /lib/systemd/system
    ln openvpn@.service openvpn@ccrypto.service

Démarrez OpenVPN :

    systemctl start openvpn@ccrypto.service

Maintenant, vous pouvez le faire démarrer en même temps que l'OS
si vous le souhaitez :

    systemctl enable openvpn@ccrypto.service


Debian/Ubuntu
-------------
**Vous devez être connecté en tant que root pour démarrer le VPN.
Il est aussi possible d'utiliser sudo.**  

Installez OpenVPN :

    apt-get install openvpn resolvconf

Placez le fichier que vous avez téléchargé dans `/etc/openvpn/`.  
Par exemple : `/etc/openvpn/ccrypto.conf`

Démarrez OpenVPN :

    service openvpn start ccrypto

Pour le démarrer en même temps que l'OS, enregistrez vos identifiants comme
expliqué dans la partie en dessous, et éditez `/etc/default/openvpn` pour
décommenter et modifiez la ligne `AUTOSTART`:

    AUTOSTART="ccrypto"
    
Linux Mint Mate Edition 17 ou plus récent
-------------

Pré-requis: Mettez à jour votre système en utilisant la commande:

```
sudo aptitude update
```

Installez les différents programmes utilisés pour faire fonctionner votre VPN CCrypto:

```
sudo aptitude install openvpn resolvconf network-manager-openvpn-gnome
```

Redémarrez la machine pour finaliser l'installation.

Il faut maintenant télécharger le fichier de configuration disponible [sur le site dans la partie account](https://vpn.ccrypto.org/account/).
et le placer dans /etc/openvpn. Téléchargez le fichier ca.crt [disponible ici](https://vpn.ccrypto.org/ca.crt) et placez le dans /etc/openvpn.

Il s'agit d'un fichier .ovpn (qui fonctionne tel que sous Windows). Un simple renommage de ce fichier en ccrypto-*.conf suffit a faire fonctionner le tout.

- On clique gauche sur l'icône réseau du Tableau de bord > Connexions Réseaux > Ajouter
- Sélectionnez "importez une configuration VPN enregistrée"
- On va dans le répertoire /etc/openvpn/ et on sélectionne le fichier ccrypto-*.conf.
La fenêtre suivante devrait s'afficher: ![screenshot](http://i.imgur.com/HcdRwgP.png)

Choisissez Mot de passe comme type d'authentification. Rentrez votre nom d'utilisateur ainsi que votre mot de passe
Et dans certificat du CA, sélectionnez  votre ca.crt téléchargé précedemment.

Votre VPN est prêt à l'utilisation.

Enregistrer les identifiants
----------------------------
Vous pouvez faire qu'OpenVPN enregistre votre nom d'utilisateur et votre mot de
passe, pour ne pas avoir à l'entrer à chaque connexion.

Créez un fichier texte "ccrypto_creds.txt" contenant votre nom sur la
première ligne, et votre mot de passe sur la deuxième, comme ceci:

    JackSparrow
    s0mep4ssw0rd

Déplacez-le ensuite dans `/etc/openvpn/`, avec le fichier
ccrypto.conf que vous avez téléchargé plus tôt.

Ouvrez ccrypto.ovpn avec un éditeur de texte (vim, gedit, kate, ...)
et ajouter une ligne à la fin:

    auth-user-pass /etc/openvpn/ccrypto_creds.txt

Pour que seul root puisse lire ce fichier :

    chown root:root /etc/openvpn/ccrypto_creds.txt
    chmod 600 /etc/openvpn/ccrypto_creds.txt

Autres distributions
--------------------

Vous devriez lire un guide adapté à la distribution :

* <a href="https://wiki.archlinux.org/index.php/OpenVPN">ArchLinux</a>


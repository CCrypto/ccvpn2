Title: Auto-Diagnostic

J'ai un fichier ".ovpn" mais il me faut un ".conf" !
--------
Il vous suffit de changer l'extension en renommant le fichier.

Il m'est impossible d'utiliser votre VPN avec Network-Manager.
--------
Tout d'abord, vérifiez que vous avez correctement créé le profil (tutoriel à venir).
Si c'est bien le cas, avant toute chose, vérifiez qu'OpenVPN lui-même est opérationnel en utilisant cette commande :
`sudo openvpn --config ccrypto.conf`
(assurez-vous de remplacer "ccrypto.conf" par le nom de votre fichier de configuration)

Je suis connecté mais je ne peux pas ping google.com o_o
--------
Essayez de `ping 8.8.8.8`, si ça marche, votre ordinateur n'utilise pas le serveur DNS. Ajoutez `nameserver 10.99.0.20` au début de /etc/resolv.con **une fois la connexion établie**. Sinon, lisez la suite.

Ça ne marche toujours pas !
--------
En utilisant la commande `ip r` (abbrégé pour `ip route`), vérifiez que vous avez, entre autre choses, les lignes suivantes :
> `0.0.0.0/1 via 10.99.2.1 dev tun0`
> `10.99.0.0/24 via 10.99.2.1 dev tun0`
> `10.99.2.0/24 dev tun0  proto kernel  scope link  src 10.99.2.18`
> `128.0.0.0/1 via 10.99.2.1 dev tun0`
> `199.115.114.65 via 192.168.1.1 dev wlan0`
Ces valeurs peuvent (et pour certaines, vont) changer suivant votre configuration (par exemple : wlan0 → eth0, 192.168.1.1 → 192.168.42.23, etc.)
Si vous n'avez pas toutes ces lignes, relancez OpenVPN ou ajouter les routes à la main en utilisant `ip r a` (`ip route add`). Si vous ne savez pas comment fair, ce serait mieux de venir nous demander sur IRC (nous allons avoir besoin des sorties des commandes `ip a` (`ip address`) et `ip r`, veuillez utiliser https://paste.cubox.me et nous envoyer uniquement le lien vers le paste).

J'ai tout essayé mais rien ne semble fonctionner ! T_T
---------
Ok… Je pense que vous pouvez venir [nous demander sur IRC](https://kiwiirc.com/client/chat.freenode.net/?nick=ccvpn|?&theme=cli#ccrypto) (mais souvenez-vous que nous ne sommes pas des professionnels payés, nous ne sommes pas toujours présent mais nous finirons toujours par répondre si vous ne partez pas trop vite).


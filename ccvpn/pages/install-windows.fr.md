Title: Installation sous Windows

Tout d'abord, il vous faut télécharger et installer OpenVPN, disponible ici:
[OpenVPN.net](http://openvpn.net/index.php/open-source/downloads.html)  
Récupérez le `Windows Installer` et lancez-le.


Dans [votre compte](/account/), téléchargez le fichier .ovpn que vous voulez
et placez-le dans `C:\Program Files\OpenVPN\config\`.

Pour commencer à utiliser le VPN, démarrez `OpenVPN GUI` **en tant qu'administrateur**.
Dans la zone de notification, vous devriez voir une icône OpenVPN :
Faites un clic droit dessus, et cliquez sur `Connect`.


Enregistrer les identifiants
----------------------------
Vous pouvez faire qu'OpenVPN enregistre votre nom d'utilisateur et votre mot de
passe, pour ne pas avoir à l'entrer à chaque connexion.

Créez un fichier texte "ccrypto_creds.txt" contenant votre nom sur la
première ligne, et votre mot de passe sur la deuxième, comme ceci:

    JackSparrow
    s0mep4ssw0rd

Déplacez-le ensuite dans `C:\Program Files\OpenVPN\config\`, avec le fichier
ccrypto.ovpn que vous avez téléchargé plus tôt.

Ouvrez ccrypto.ovpn avec un éditeur de texte (Bloc-notes, Notepad++, ...)
et ajouter une ligne à la fin:

    auth-user-pass ccrypto_creds.txt

Pour finir, redémarrez OpenVPN GUI et connectez vous : il ne devrait plus vous
demander votre mot de passe.



Résolution de problèmes
-----------------------

Tout d'abord, assurez vous d'avoir bien démarré OpenVPN en tant qu'administrateur
et que ccrypto.ovpn est correctement placé dans `C:\Program Files\OpenVPN\config\`.  


### netsh.exe

Si vous trouvez ces lignes dans votre historique OpenVPN:

    NETSH: C:\Windows\system32\netsh.exe interface ipv6 set address Connexion au réseau local
    ERROR: netsh command failed: returned error code 1

Cette erreur est fréquente sous windows et semble arriver à cause d'un problème
d'OpenVPN avec netsh.exe et l'IPv6.
Pour le résoudre, renommez votre connection réseau pour éviter les espaces.
Par exemple « Connexion au réseau local » en « lan ».

  - [(fr) Renommer une connexion réseau](http://windows.microsoft.com/fr-xf/windows-vista/rename-a-network-connection)


### Multiples interfaces TAP
    Error: When using --tun-ipv6, if you have more than one TAP-Windows adapter, you must also specify --dev-node
    Exiting due to fatal error

Cette erreur pourra apparaitre si vous avec de multiples interfaces TAP,
la plupart du temps à cause d'un autre logiciel utilisant TAP.
Pour le résoudre, ouvrez un interpréteur de commandes (Shift + Clic droit)
dans votre répertoire OpenVPN (là où openvpn.exe se situe) et lancez :

    openvpn.exe --show-adapters

Cela va lister vos interfaces TAP.
Puis, ouvrez votre fichier de configuration ccrypto.ovpn avec un éditeur de texte
et ajoutez ceci sur une nouvelle ligne :

    dev-node [nom]

Remplacez [nom] par le nom de votre interface TAP.


### Ça ne fonctionne toujours pas ?

Si vous ne pouvez toujours pas utiliser le VPN, n'hésitez pas à
[nous contacter](/page/help).
Joignez les logs d'OpenVPN à votre message, pour nous aider à trouver
le problème au plus vite.



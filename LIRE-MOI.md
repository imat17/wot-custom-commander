# Custom Commander — version 0.2.5 alpha

Conçu pour votre installation **World of Tanks EU 2.4.1.1**, avec Aslain Mod Menu et OpenWG Gameface déjà présents. Tests automatisés hors jeu ; le résultat visuel et sonore doit encore être vérifié dans le jeu. Cette alpha ne remplace aucun fichier d’un autre mod, notamment Classic Tank Carousel.

## Essai dans le garage

1. Redémarrez le jeu après installation.
2. Faites un clic droit sur le chef de char dans le panneau d’équipage et choisissez **Utiliser Papacito** (ou **Utiliser Profil personnel / démonstration**).
3. La photo du profil choisi doit remplacer son portrait dans ce panneau. Les autres équipiers conservent leur apparence. Pour Papacito, la fiche personnelle utilise aussi le portrait et le nom locaux. Le profil personnel / démonstration conserve son affichage expérimental dans le garage.
4. Dans le menu des mods du garage, ouvrez **Custom Commander**. Choisissez **Papacito** dans **Profil à écouter / appliquer**, puis cliquez sur **Écouter** pour sa réplique de départ. Le profil personnel utilise les médias de démonstration lorsque sa case dédiée est cochée.
5. Refaire un clic droit puis **Retirer la personnalisation** rétablit le portrait d’origine et les prochaines annonces vocales d’origine. Le menu des réglages propose aussi **Appliquer** et **Retirer** pour le chef du char sélectionné. Un profil déjà actif reste actif si vous le choisissez une deuxième fois.

Les sélections sont enregistrées localement par compte et par identifiant de membre d’équipage. Il n’y a aucune requête de modification d’identité, de compétence ou d’apparence vers le serveur. L’interrupteur général masque les personnalisations sans effacer les sélections.

## Profil Papacito intégré

Clic droit sur un chef de char dans le garage → **Utiliser Papacito**. Le nom Papacito identifie le profil et remplace le nom affiché par les écrans utilisant la présentation du chef de char ; l’identité officielle sur le compte reste inchangée. La photo JPEG fournie est conservée sans modification. Les MP3 sont convertis en WAV PCM 16 bits mono, sans coupe.

| Fichier fourni | Action associée |
|---|---|
| papacito_start.mp3 | Début de bataille |
| papacito_penetration.mp3 | Votre tir pénètre et inflige des dégâts à un ennemi |
| papacito_ricochet.mp3 | Votre tir ricoche ou ne perce pas le blindage ennemi |
| papacito_destruction.mp3 | Ennemi détruit par vous |
| papacito_dead.mp3 | Votre propre char détruit |
| papacito_chenilles.mp3 | Vos chenilles détruites |
| papacito_chenilles_fix.mp3 | Vos chenilles réparées |

Les sept répliques sont installées sous huit fichiers WAV (la réplique de ricochet est aussi utilisée pour le blindage non percé) dans `mods/configs/matisse.commander_friend/profiles/papacito/voice/`. Les autres événements conservent la voix du jeu. Les correspondances et les durées figurent aussi dans `profiles/papacito/profile.json`. Les anciennes sélections restent associées au profil personnel ; aucune activation automatique de Papacito.

## Six enregistrements pour commencer

| Situation | Fichier WAV | Exemple de phrase libre |
|---|---|---|
| Départ | `vo_start_battle.wav` | En route ! |
| Tir pénétrant | `vo_enemy_hp_damaged_by_projectile_by_player.wav` | Bien touché ! |
| Ricochet | `vo_armor_ricochet_by_player.wav` | Ça a ricoché ! |
| Ennemi détruit par vous | `vo_enemy_killed_by_player.wav` | Un de moins ! |
| Chenilles cassées | `vo_track_destroyed.wav` | On est immobilisés ! |
| Chenilles réparées | `vo_track_functional.wav` | On peut repartir ! |

Déposez-les dans `G:/Jeux/World_of_Tanks_EU/mods/configs/matisse.commander_friend/voice/` : **WAV PCM 16 bits, mono ou stéréo, durée supérieure à zéro et au maximum 15 secondes**. Les fichiers manquants ou invalides laissent passer la voix native. Vous pouvez enregistrer vos propres phrases ; il ne faut pas recopier un texte officiel.

Le bouton **Liste des répliques à enregistrer** ouvre le catalogue complet. Il contient 392 entrées des cinq tables de notifications installées, dont 316 vocales et 295 noms de fichiers distincts. Ce nombre englobe les communications et les modes spéciaux ; vous n’avez pas besoin de tous les enregistrer. Les descriptions de certains modes sont encore à confirmer. Les variantes parlées à l’intérieur des banques Wwise et les sons extérieurs à ces tables ne sont pas inventoriés.

## Votre photo

Dans les réglages, ouvrez **Dossier de la photo**, placez-y un portrait PNG nommé `friend.png`, puis désactivez **Utiliser les médias de démonstration** et appliquez. Redémarrez le client après avoir ajouté ou remplacé l’image si elle ne se recharge pas. Le fichier se trouve dans `res_mods/2.4.1.1/gui/maps/icons/commander_friend/friend.png`. Une image carrée est préférable. Cette version conserve deux profils distincts : Papacito et le profil personnel / démonstration. Chaque chef activé conserve le profil que vous lui avez attribué. La photo friend.png appartient uniquement au profil personnel.

## Audio de cette alpha

Le jeu sélectionne la notification et applique ses tests de file d’attente avant le remplacement. Les effets sonores restent traités par le jeu. L’alpha utilise le lecteur WAV Windows et avance la file après la durée du fichier ; elle ne produit pas encore de banque Wwise. Le volume personnalisé dépend du mélangeur Windows et n’est pas synchronisé avec le curseur des voix WoT. Les sous-titres personnalisés ne sont pas fournis.

Les replays sont exclus. Le remplacement est limité au véhicule dont le chef activé a été identifié dans le garage ; spectateur et véhicule différent laissent passer le comportement natif. Les modes avec changements de véhicule et les interactions avec d’autres mods vocaux nécessitent un test. Les notifications remplacées contournent la diffusion vocale VSE de ces seules entrées : un mod qui s’abonne à cet événement ne reçoit pas les entrées remplacées.

## Installation et retour en arrière

`Installer.ps1` vérifie la version du jeu et les dépendances avant de copier le paquet. Il refuse une installation pendant que le jeu tourne. Il met à jour les versions 0.1.0, 0.1.1 et 0.2.0 connues en la conservant dans le dossier de sauvegardes du mod ; une version inconnue est refusée. Le petit lecteur audio Windows fourni est installé dans le sous-dossier native_0.1.1 de la configuration. `Desinstaller.ps1` retire uniquement le paquet inchangé, en conservant vos médias et choix.

L’alpha n’est pas ajoutée à la réinstallation automatique d’Aslain : cela évite son report automatique vers une future version du jeu non vérifiée. Une installation propre du modpack peut donc la retirer.

## Validation restante

- Apparition du menu **Custom Commander** et du choix au clic droit.
- Activation/désactivation du portrait, changement de char puis redémarrage.
- Écoute de démonstration et lecture en bataille sur un chef activé.
- Absence de changement sur un chef non activé et retour aux voix natives si un WAV manque.

Les erreurs éventuelles sont consignées dans le journal du jeu sous `CommanderFriend`. Le développement n’a ni lancé une bataille ni contrôlé votre compte.

## Correctif 0.1.1

Les deux actions échouaient dans le jeu parce que `_ctypes` était absent : le clic droit annulait la sélection et le bouton Écouter ne lançait aucun son. La sauvegarde utilise désormais les fonctions de fichiers Python avec copie de récupération ; la lecture passe par un petit module Windows compilé fourni avec le mod, sans ctypes. Les tests reproduisent cette absence et vérifient la lecture WAV, les changements de sélection et la récupération après une sauvegarde interrompue. Ils passent aussi avec une copie du moteur Python de votre jeu dans un programme de test isolé. La validation des clics, du portrait et du son dans le garage reste à effectuer après redémarrage.

## Correctif 0.2.1

La réplique de ricochet couvre aussi les notifications de blindage non percé, y compris leurs variantes répétées. Les événements sans dégâts liés uniquement à un module ou à une explosion gardent leur son d’origine. Le retour au garage ignore désormais les panneaux d’équipage temporairement sans modèle pour permettre au panneau actif de recevoir le portrait. Chaque réplique personnalisée lancée est identifiée dans le journal par `CommanderFriend` et `Voice played`. Le journal confirme la demande de lecture, pas le son effectivement entendu.

Les répliques Papacito sont préparées à 80 % de leur amplitude initiale (baisse demandée de 20 %), sans modification de durée. Les MP3 originaux restent inchangés.

## Correctif 0.2.2 — portrait natif

Papacito fournit maintenant son nom et sa photo aux fonctions de présentation utilisées par le garage et la fiche personnelle. Les ressources sont disponibles pour un chef standard ou déjà équipé d’une apparence. Le descripteur du membre d’équipage et l’apparence officielle ne sont pas modifiés. À la désactivation, les fonctions d’origine fournissent à nouveau le portrait et le nom. Si une ressource manque, le mod conserve l’apparence d’origine et le signale dans le journal. Le menu Aslain passe au schéma 2 pour afficher les nouveaux contrôles ; les sélections de chefs sont conservées, les cases et le profil d’aperçu reviennent à leurs valeurs par défaut.

## Correctif 0.2.3 — déclaration des ressources

Le fichier `gui/gen_resources/matisse.commander_friend.json` déclare les deux identifiants de portrait, leur type Image et leur chemin img://, selon le format du catalogue livré avec WoT 2.4.1.1. Cette déclaration manquait en 0.2.2, et le journal indiquait que les ressources natives étaient indisponibles. Un contrôle du paquet vérifie désormais les identifiants, les chemins et les octets de la photo. Le volume est désormais à 64 % du niveau d’origine.

## Correctif 0.2.4 — retour au portrait original

La désactivation réécrit le portrait, le nom et l’indicateur d’apparence dans les modèles d’équipage encore affichés, puis invalide leur liste dans une transaction native. La fiche personnelle ouverte est rafraîchie avec ComponentBase.refreshView, qui publie les changements du modèle parent. Cela évite de dépendre du contrôleur initial du garage ou de modifier seulement des valeurs Python sans actualiser l’écran. La désactivation du profil, du portrait ou du mod rétablit les données natives actuelles du chef de char. Les compteurs `Portrait refresh committed` permettent de vérifier les mises à jour dans les logs.

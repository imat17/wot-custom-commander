# Chef de char ami — version 0.1.1 alpha

Conçu pour votre installation **World of Tanks EU 2.4.1.1**, avec Aslain Mod Menu et OpenWG Gameface déjà présents. Tests automatisés hors jeu ; le résultat visuel et sonore doit encore être vérifié dans le jeu. Cette alpha ne remplace aucun fichier d’un autre mod, notamment Classic Tank Carousel.

## Essai dans le garage

1. Redémarrez le jeu après installation.
2. Faites un clic droit sur le chef de char dans le panneau d’équipage et choisissez **Activer la personnalisation ami**.
3. Un portrait de démonstration doit remplacer son portrait dans ce panneau. Les autres équipiers conservent leur apparence. Le dossier personnel, les infobulles et les autres écrans ne sont pas encore personnalisés.
4. Dans le menu des mods du garage, ouvrez **Chef de char ami**. Le bouton **Écouter** joue une réplique synthétique de démonstration. Il ne s’agit pas de la voix de votre ami.
5. Refaire un clic droit puis **Retirer la personnalisation ami** rétablit le portrait d’origine et les prochaines annonces vocales d’origine. Le menu des réglages propose aussi cette bascule pour le chef du char sélectionné.

Les sélections sont enregistrées localement par compte et par identifiant de membre d’équipage. Il n’y a aucune requête de modification d’identité, de compétence ou d’apparence vers le serveur. L’interrupteur général masque les personnalisations sans effacer les sélections.

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

Dans les réglages, ouvrez **Dossier de la photo**, placez-y un portrait PNG nommé `friend.png`, puis désactivez **Utiliser les médias de démonstration** et appliquez. Redémarrez le client après avoir ajouté ou remplacé l’image si elle ne se recharge pas. Le fichier se trouve dans `res_mods/2.4.1.1/gui/maps/icons/commander_friend/friend.png`. Une image carrée est préférable. Cette alpha propose un profil d’ami commun aux chefs activés, pas encore plusieurs amis avec une photo différente chacun.

## Audio de cette alpha

Le jeu sélectionne la notification et applique ses tests de file d’attente avant le remplacement. Les effets sonores restent traités par le jeu. L’alpha utilise le lecteur WAV Windows et avance la file après la durée du fichier ; elle ne produit pas encore de banque Wwise. Le volume personnalisé dépend du mélangeur Windows et n’est pas synchronisé avec le curseur des voix WoT. Les sous-titres personnalisés ne sont pas fournis.

Les replays sont exclus. Le remplacement est limité au véhicule dont le chef activé a été identifié dans le garage ; spectateur et véhicule différent laissent passer le comportement natif. Les modes avec changements de véhicule et les interactions avec d’autres mods vocaux nécessitent un test. Les notifications remplacées contournent la diffusion vocale VSE de ces seules entrées : un mod qui s’abonne à cet événement ne reçoit pas les entrées remplacées.

## Installation et retour en arrière

`Installer.ps1` vérifie la version du jeu et les dépendances avant de copier le paquet. Il refuse une installation pendant que le jeu tourne. Il met à jour la version 0.1.0 connue en la conservant dans le dossier de sauvegardes du mod ; une version inconnue est refusée. Le petit lecteur audio Windows fourni est installé dans le sous-dossier native_0.1.1 de la configuration. `Desinstaller.ps1` retire uniquement le paquet inchangé, en conservant vos médias et choix.

L’alpha n’est pas ajoutée à la réinstallation automatique d’Aslain : cela évite son report automatique vers une future version du jeu non vérifiée. Une installation propre du modpack peut donc la retirer.

## Validation restante

- Apparition du menu **Chef de char ami** et du choix au clic droit.
- Activation/désactivation du portrait, changement de char puis redémarrage.
- Écoute de démonstration et lecture en bataille sur un chef activé.
- Absence de changement sur un chef non activé et retour aux voix natives si un WAV manque.

Les erreurs éventuelles sont consignées dans le journal du jeu sous `CommanderFriend`. Le développement n’a ni lancé une bataille ni contrôlé votre compte.

## Correctif 0.1.1

Les deux actions échouaient dans le jeu parce que `_ctypes` était absent : le clic droit annulait la sélection et le bouton Écouter ne lançait aucun son. La sauvegarde utilise désormais les fonctions de fichiers Python avec copie de récupération ; la lecture passe par un petit module Windows compilé fourni avec le mod, sans ctypes. Les tests reproduisent cette absence et vérifient la lecture WAV, les changements de sélection et la récupération après une sauvegarde interrompue. Ils passent aussi avec une copie du moteur Python de votre jeu dans un programme de test isolé. La validation des clics, du portrait et du son dans le garage reste à effectuer après redémarrage.

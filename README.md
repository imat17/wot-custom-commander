# Custom Commander

Custom Commander est un mod pour **World of Tanks** qui permet de personnaliser localement le portrait et certaines annonces vocales d’un chef de char. Il propose un profil Papacito et un profil personnel / de démonstration.

> **Version 0.2.5 alpha** : prévue pour World of Tanks EU **2.4.1.1**, sous Windows. Le comportement visuel et sonore doit encore être vérifié en jeu, notamment après une mise à jour du client.

## Fonctionnalités

- Choisir un profil pour chaque chef de char depuis le garage et revenir à son apparence d’origine.
- Afficher le portrait et le nom locaux de Papacito dans le garage et sa fiche personnelle.
- Remplacer certaines annonces vocales par les répliques du profil. Les événements sans fichier valide conservent leur voix d’origine.
- Utiliser une photo et des enregistrements personnels avec le profil dédié.

Les choix sont enregistrés localement par compte et par membre d’équipage. Le mod ne modifie pas l’identité, les compétences ou l’apparence officielles sur le serveur.

## Installation

**Prérequis :** World of Tanks EU 2.4.1.1, **Aslain Mod Menu** et **OpenWG Gameface** installés. Fermez le jeu avant toute installation.

1. Téléchargez [l’archive Custom Commander 0.2.5 alpha](dist/Custom-Commander-0.2.5-alpha.zip) depuis GitHub, puis décompressez-la entièrement.
2. Ouvrez PowerShell dans le dossier décompressé.
3. Lancez la commande suivante en remplaçant le chemin par celui de votre installation du jeu :

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\Installer.ps1 -GameRoot "G:\Jeux\World_of_Tanks_EU"
   ```

L’installateur vérifie la version et les dépendances, et sauvegarde les fichiers du profil qu’il remplace. Une version inconnue du mod peut nécessiter une intervention manuelle.

## Utilisation

1. Lancez le jeu et ouvrez le garage.
2. Faites un clic droit sur un chef de char et sélectionnez **Utiliser Papacito** ou **Utiliser Profil personnel / démonstration**.
3. Dans le menu des mods, ouvrez **Custom Commander** pour choisir un profil, l’appliquer ou écouter un aperçu.
4. Pour revenir à l’apparence et aux voix d’origine, faites un nouveau clic droit et choisissez **Retirer la personnalisation**.

Le profil Papacito comprend sept répliques pour le départ, les tirs, les destructions et les chenilles. Son volume est réglé à 64 % de l’amplitude des enregistrements d’origine. Le volume du mod dépend également du mélangeur Windows et ne suit pas le curseur des voix de WoT.

## Profil personnel

Dans les réglages, ouvrez **Dossier de la photo**, ajoutez une image carrée PNG nommée `friend.png`, puis désactivez les médias de démonstration et appliquez. Un redémarrage du jeu peut être nécessaire.

Placez vos enregistrements dans `mods/configs/matisse.commander_friend/voice/`. Ils doivent être au format **WAV PCM 16 bits**, mono ou stéréo, et durer entre zéro et 15 secondes. Le catalogue et les noms des fichiers sont décrits dans [LIRE-MOI.md](LIRE-MOI.md).

## Limites et désinstallation

Les replays sont exclus. Les changements de véhicule et les interactions avec d’autres mods vocaux restent à vérifier. Les sous-titres personnalisés ne sont pas disponibles. Une mise à jour du jeu peut rendre le mod incompatible.

Pour désinstaller, fermez le jeu puis exécutez `Desinstaller.ps1` avec le même paramètre `-GameRoot` que pour l’installation. Le script retire le paquet inchangé et conserve les médias et les sélections.

Consultez [LIRE-MOI.md](LIRE-MOI.md) pour le fonctionnement détaillé, les fichiers audio et les notes de version.

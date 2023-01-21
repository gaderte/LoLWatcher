# LoLWatcher
Bot Discord - LoL Watcher

Requirements : discord.py, requests, mysql_connector_python

Required Discord Perm = "Send Message"

Host : SparkedHost

Url to add the bot (need Admin perm) : https://discord.com/api/oauth2/authorize?client_id=945415340324704277&permissions=2048&scope=bot

French :

Comment utiliser le bot :
  - Il faut impérativement aller dans les paramètres du serveur => Intégrations => LoLWatcher et changer les permissions des commandes.
  - Lancer la commande "initialize" pour setup le bot. Il y a deux paramètres dont 1 facultatif :
    - "channelmessage" : le channel où seront envoyés les messages concernant l'elo
    - "roleaping" (facultatif) : le rôle qui sera ping à chaque nouvelle notification. Laissez vide si pas de role
  - Un membre peut utiliser la commande "addjoueur" pour s'ajouter dans la liste (1 compte LoL par membre)
  - Un membre peut utiliser la commande "leavelolwatcher" pour se retirer de la liste
  - La commande "listjoueurs" permet d'afficher tous les joueurs inscrits sur votre serveur

Si un joueur est kick ou ban du serveur, le bot clear automatiquement son compte
Si le bot est kick ou ban du serveur, il clear automatiquement tous les comptes associés

/!\ La clé étant limité en requête, essayez de ne pas ajouter + de 15 joueurs par serveur /!\

/!\ Avant d'ajouter un joueur, soyez sûr que le pseudo est bien orthographié et que le joueur a fini ses games de placements /!\

Contactez moi sur Discord au besoin : DRX Atlas#6180


English :

How to use :
  - Go to Guild params and change slash commands permissions to secure bot usage
  - Launch "initialize" command to set-up the bot. It only needs 1 parameter :
    - "channelmessage" : enter the channel where the bot will display elo change messages
    - "roleaping" (optional) : enter a role to ping each time a message is displayed. Leave blank if not needed
  - A discord member can use the command "addjoueur" to add himself (1 account per member)
  - A discord member can use the command "leavelolwatcher" to remove himself
  - "listjoueurs" is a command to display all players register on your server

if you kick or ban the bot => clear all players
if a player leave your guild => clear from players list

/!\ Try to not add more than 15 players per server. /!\ 

/!\ Before adding, make sure you finished your placements games /!\

Contact me on Discord if needed : DRX Atlas#6180

Enjoy

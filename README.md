# LoLWatcher
Bot Discord - LoL Watcher

Requirements : discord.py, requests, mysql_connector_python
Required Discord Perm = "Send Message"
Host : SparkedHost

Url to add (need Admin perm) : https://discord.com/api/oauth2/authorize?client_id=945415340324704277&permissions=2048&scope=bot

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

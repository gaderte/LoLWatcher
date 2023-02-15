import discord
import requests
from discord.ext import tasks, commands
from Database import Database

compteur = 0

riot_api_key = "X"
TOKEN = "X"

db = Database()
intents = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=intents)

tiers = {
    "IRON": 1,
    "BRONZE": 2,
    "SILVER": 3,
    "GOLD": 4,
    "PLATINUM": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9
}
ranks = {
    "IV": 1,
    "III": 2,
    "II": 3,
    "I": 4,
}


def displayInfo(player, guildid):
    refreshedPlayer = db.recoverSpecificJoueur(player[0], guildid)
    temp = "Le joueur " + refreshedPlayer[1] + " est classé " + str(refreshedPlayer[2]) + " " + \
           str(refreshedPlayer[3]) + " avec " + str(refreshedPlayer[4]) + " LPs."
    if refreshedPlayer[5] == 1:
        x = refreshedPlayer[6].replace('W', ":white_check_mark: ")\
            .replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
        temp += "\nLe joueur est actuellement en BO : " + x
    return temp


def createPlayer(acc, rank, guild, member_id):
    for typegames in rank:
        if typegames.get('queueType') == "RANKED_SOLO_5x5":
            if typegames.get('miniSeries') is not None:
                prog = typegames.get('miniSeries')
                progress = prog.get('progress')
                enBo = True
            else:
                progress = ""
                enBo = False
            rc = db.addJoueur(acc.get('id'), acc.get('name'), typegames.get('tier'), typegames.get('rank'),
                              typegames.get('leaguePoints'), enBo, progress, guild.id, member_id)
            return rc


def addPlayer(summonername, guild, member_id):
    urlSummoners = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonername + \
                   '?api_key=' + riot_api_key
    r = requests.get(urlSummoners)
    if r.status_code != 200:
        print("Code erreur : " + str(r.status_code))
        print("Erreur API Riot.")
        return None
    account = r.json()
    urlRanks = 'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + account.get('id') + \
               '?api_key=' + riot_api_key
    r = requests.get(urlRanks)
    ranking = r.json()
    if r.status_code != 200:
        print("Erreur API Riot.")
        return None
    nbr = createPlayer(account, ranking, guild, member_id)
    return nbr


def check_rang(player, guild):
    urlRanks = 'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + player[0] + \
               '?api_key=' + riot_api_key
    r = requests.get(urlRanks)
    ranking = r.json()
    if r.status_code != 200:
        print("Code erreur : " + str(r.status_code))
        print("Erreur API Riot.")
        return None
    for typequeue in ranking:
        if typequeue.get('queueType') == 'RANKED_SOLO_5x5':
            ret = ""
            atmelo = {
                "summonername": player[1],
                "tier": player[2],
                "rank": player[3],
                "lps": player[4],
                "enBo": player[5],
                "progress": player[6]
            }
            if guild[3] != 0:
                ret += "<@&" + str(guild[3]) + "> "
            if typequeue.get('miniSeries') is not None:
                atmelo["enBo"] = True
                miniS = typequeue.get('miniSeries')
                progress = miniS.get('progress')
                if progress != atmelo["progress"]:
                    db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'),
                                    typequeue.get('rank'),
                                    typequeue.get('leaguePoints'), atmelo.get("enBo"), progress)
                    return ret
            else:
                atmelo["enBo"] = False
            if typequeue.get('tier') == atmelo.get("tier") and typequeue.get('rank') == atmelo.get("rank") and \
                    typequeue.get('leaguePoints') == atmelo.get("lps"):
                return "RAS"
            if typequeue.get('tier') != atmelo.get("tier") \
                    and tiers.get(typequeue.get('tier')) < tiers.get(atmelo.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a derank de " + atmelo.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret
            if typequeue.get('tier') != atmelo.get("tier") \
                    and tiers.get(typequeue.get('tier')) > tiers.get(atmelo.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a rank up de " + atmelo.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret

            if typequeue.get('rank') != atmelo.get("rank") \
                    and ranks.get(typequeue.get('rank')) < ranks.get(atmelo.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est descendu de " + atmelo.get("tier") + ' ' + \
                       atmelo.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret
            if typequeue.get('rank') != atmelo.get("rank") \
                    and ranks.get(typequeue.get('rank')) > ranks.get(atmelo.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est monté de " + atmelo.get("tier") + ' ' + \
                       atmelo.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret

            if typequeue.get('leaguePoints') != atmelo.get("lps") and typequeue.get('leaguePoints') < atmelo.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a perdu -" + \
                       str(atmelo.get("lps") - typequeue.get('leaguePoints')) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret
            if typequeue.get('leaguePoints') != atmelo.get("lps") and typequeue.get('leaguePoints') > atmelo.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a gagné +" + \
                       str(typequeue.get('leaguePoints') - atmelo.get("lps")) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), atmelo.get("enBo"), atmelo.get("progress"))
                return ret


@client.event
async def on_ready():
    print('Connecté en tant que')
    print(client.user.name)
    print(client.user.id)
    print('-------')
    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(
            f'{guild.name}(id: {guild.id})'
        )
    print("Synchro du tree...")
    await client.tree.sync()
    await client.wait_until_ready()
    print("Chargement de l'activité...")
    await client.change_presence(activity=discord.Game(name="Je vous vois tous"))
    on_update.start()


@client.event
async def on_guild_join(guild):
    db.addServeur(guild.id, guild.name, 0, 0)
    return


@client.event
async def on_guild_remove(guild):
    db.removeServeur(guild.id)
    db.removeAllJoueurs(guild.id)
    return


@client.event
async def on_raw_member_remove(payload):
    db.RemoveJoueur(payload.guild_id, payload.user.id)
    return


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    await client.process_commands(message)


@client.tree.command(name="initialize", description="Initialise un nouveau serveur")
async def initialize(ints, channelmessage: discord.TextChannel,
                     roleaping: discord.Role = None):
    try:
        msg = "Message test. Si vous voyez ce message, cela signifie que le bot a l'autorisation d'écrire dans le " \
              "channel. Vous pouvez le supprimer dès la fin de l'initialisation."
        await channelmessage.send(msg)
    except discord.errors.Forbidden:
        msg = "Le bot n'a pas l'autorisation d'écrire dans le channel : " + channelmessage.name + \
              ". Veuillez changer de channel ou accorder les autorisations avant de recommencer."
        await ints.response.send_message(msg)
        return
    else:
        if not roleaping:
            roleaping = 0
            db.InitializeServer(ints.guild_id, channelmessage.id, roleaping)
        else:
            db.InitializeServer(ints.guild_id, channelmessage.id, roleaping.id)
        await ints.response.send_message("Le serveur a bien été initialisé")


@client.tree.command(name="addjoueur", description="S'ajouter dans la liste des joueurs")
async def addJoueur(ints, nomjoueur: str):
    ret = addPlayer(nomjoueur, ints.guild, ints.user.id)
    if ret is None:
        msg = "Erreur lors de l'ajout du joueur. Veuillez vérifier qu'il existe bien, qu'il est niveau 30 et qu'il" \
              " a fini ses games de placements."
        await ints.response.send_message(msg)
    elif ret == 1:
        await ints.response.send_message("Vous avez bien été ajouté à la liste.")
    elif ret == 2:
        await ints.response.send_message("Vous êtes déjà dans la liste du Bot.")
    else:
        print("Erreur lors de l'ajout.")


@client.tree.command(name="leavelolwatcher", description="Se retirer de la liste des joueurs")
async def removeJoueur(ints):
    res = db.RemoveJoueur(ints.guild_id, ints.user.id)
    if res == 1:
        await ints.response.send_message("Vous avez été retiré de la liste")
    else:
        await ints.response.send_message("Vous n'êtes pas présent dans la liste")


@client.tree.command(name="listejoueurs", description="Liste des joueurs")
async def listeJoueurs(ints):
    await ints.response.defer()
    res = db.GetJoueursOfGuild(ints.guild_id)
    g = ints.guild
    retour = "Liste de(s) joueur(s) : \n"
    if not res:
        retour = "La liste des joueurs est vide"
    else:
        for i in db.GetJoueursOfGuild(ints.guild_id):
            m = await g.fetch_member(i[8])
            retour += " - " + i[1] + " (" + m.name + ") \n"
        temp = retour.rsplit('\n', 1)
        retour = ''.join(temp)
    await ints.followup.send(retour)


@client.tree.command(name="infojoueur", description="Donne les infos d'un joueur")
async def info_joueur(ints, summonername: str):
    await ints.response.defer()
    p = db.GetPlayerInfo(ints.guild_id, summonername)
    if p:
        temp = "Le joueur " + p[1] + " est classé " + str(p[2]) + " " + \
               str(p[3]) + " avec " + str(p[4]) + " LPs."
        if p[5] == 1:
            x = p[6].replace('W', ":white_check_mark: ").replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
            temp += "\nLe joueur est actuellement en BO : " + x
        await ints.followup.send(temp)
    else:
        temp = "Erreur lors de la récupération du joueur. Veuillez vérifier qu'il existe bien"
        await ints.followup.send(temp)


@client.tree.command(name="infojoueurdiscord", description="Donne les infos d'un joueur")
async def info_joueur_discord(ints, membre: discord.Member):
    await ints.response.defer()
    p = db.GetPlayerInfoDiscord(ints.guild_id, membre.id)
    if p:
        temp = "Le joueur " + p[1] + " est classé " + str(p[2]) + " " + \
               str(p[3]) + " avec " + str(p[4]) + " LPs."
        if p[5] == 1:
            x = p[6].replace('W', ":white_check_mark: ").replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
            temp += "\nLe joueur est actuellement en BO : " + x
        await ints.followup.send(temp)
    else:
        temp = "Erreur lors de la récupération du joueur. Veuillez vérifier qu'il existe bien"
        await ints.followup.send(temp)


@client.tree.command(name="alert", description="Alerte tous les utilisateurs du bot")
async def alertGuilds(ints, message: str):
    if ints.user.id != admin_atlas_id:
        await ints.response.send_message("Seul l'administrateur peut utiliser cette commande")
        return
    await ints.response.defer()
    for g in db.recoverAllGuilds():
        channel = client.get_channel(g[2])
        try:
            await channel.send("Message de l'admin : \n>>> " + message)
        except Exception as e:
            print(e)
    await ints.followup.send("L'alerte a bien été envoyée")


@client.tree.command(name="alertadmin", description="Alerte l'administrateur d'un(e) potentiel(le) problème/demande")
async def alert_admin(ints, message: str):
    await ints.response.defer()
    atlas = await client.fetch_user(admin_atlas_id)
    ret = "<@" + str(ints.user.id) + "> vous a envoyé un meesage : \n\n" + message
    await atlas.send(ret)
    await ints.followup.send("Votre message a bien été envoyé. Vous serez recontacté sous peu."
                             " Merci de ne pas spam la commande")


@tasks.loop(minutes=3.0)
async def on_update():
    global compteur
    compteur += 1
    print("Vérification n°" + str(compteur))
    for g in db.recoverAllGuilds():
        channel = client.get_channel(g[2])
        for i in db.GetJoueursOfGuild(g[0]):
            retour = check_rang(i, g)
            if retour is None:
                print("Erreur RIOT API.")
            elif retour == "RAS":
                print(i[1] + " n'a pas joué de partie")
            else:
                retour += "\n" + displayInfo(i, g[0])
                try:
                    await channel.send(str(retour))
                except discord.errors.Forbidden:
                    print("Error guild '" + g[1] + "' : Le bot n'a pas le droit d'écrire dans le channel initialisé.")


client.run(TOKEN)


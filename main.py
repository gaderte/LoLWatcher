import datetime
from zoneinfo import ZoneInfo

import discord
import requests
from discord.ext import tasks, commands

from Database import Database

compteur = 0
db = Database()
admin_atlas_id = 114372984604590080
stratacademy_id = 799713691447853057
riot_api_key = "X"
TOKEN = "X"

intents = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=intents)

tiers = {
    "IRON": 1,
    "BRONZE": 2,
    "SILVER": 3,
    "GOLD": 4,
    "PLATINUM": 5,
    "EMERALD": 6,
    "DIAMOND": 7,
    "MASTER": 8,
    "GRANDMASTER": 9,
    "CHALLENGER": 10
}
ranks = {
    "IV": 1,
    "III": 2,
    "II": 3,
    "I": 4,
}


def displayInfo(player):
    return "Le joueur " + player.get("summonername") + " est classé " + str(player.get("tier")) + " " + \
           str(player.get("rank")) + " avec " + str(player.get("lps")) + " LPs."


def createPlayer(acc, rank, guild, member_id):
    for typegames in rank:
        if typegames.get('queueType') == "RANKED_SOLO_5x5":
            rc = db.addJoueur(acc.get('id'), acc.get('name'), typegames.get('tier'), typegames.get('rank'),
                              typegames.get('leaguePoints'), guild.id, member_id)
            db.AddClassement(acc.get('id'))
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
    print("Impossible de récupérer les données de chez Riot Games")
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
            eloactuel = {
                "summonername": player[1],
                "tier": player[2],
                "rank": player[3],
                "lps": player[4],
            }
            newelo = {
                "summonername": typequeue.get('summonerName'),
                "tier": typequeue.get('tier'),
                "rank": typequeue.get('rank'),
                "lps": typequeue.get('leaguePoints')
            }
            # guild[3] ==> rôle à ping
            if guild[3] != 0:
                ret += "<@&" + str(guild[3]) + "> "

            if typequeue.get('tier') == eloactuel.get("tier") and typequeue.get('rank') == eloactuel.get("rank") and \
                    typequeue.get('leaguePoints') == eloactuel.get("lps"):
                return ["RAS", newelo]
            if typequeue.get('tier') != eloactuel.get("tier") \
                    and tiers.get(typequeue.get('tier')) < tiers.get(eloactuel.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a derank de " + eloactuel.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                return [ret, newelo]
            if typequeue.get('tier') != eloactuel.get("tier") \
                    and tiers.get(typequeue.get('tier')) > tiers.get(eloactuel.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a rank up de " + eloactuel.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                db.UpdateWinClassement(player[0])
                return [ret, newelo]

            if typequeue.get('rank') != eloactuel.get("rank") \
                    and ranks.get(typequeue.get('rank')) < ranks.get(eloactuel.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est descendu de " + eloactuel.get("tier") + ' ' + \
                       eloactuel.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                return [ret, newelo]
            if typequeue.get('rank') != eloactuel.get("rank") \
                    and ranks.get(typequeue.get('rank')) > ranks.get(eloactuel.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est monté de " + eloactuel.get("tier") + ' ' + \
                       eloactuel.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                db.UpdateWinClassement(player[0])
                return [ret, newelo]

            if typequeue.get('leaguePoints') != eloactuel.get("lps") and typequeue.get('leaguePoints') < \
                    eloactuel.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a perdu -" + \
                       str(eloactuel.get("lps") - typequeue.get('leaguePoints')) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                return [ret, newelo]
            if typequeue.get('leaguePoints') != eloactuel.get("lps") and typequeue.get('leaguePoints') > \
                    eloactuel.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a gagné +" + \
                       str(typequeue.get('leaguePoints') - eloactuel.get("lps")) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'))
                db.UpdateWinClassement(player[0])
                return [ret, newelo]


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
    classement.start()


@client.event
async def on_guild_join(guild):
    print("GuildAdd : le bot a été ajouté sur un serveur")
    db.addServeur(guild.id, guild.name, 0, 0)
    return


@client.event
async def on_guild_remove(guild):
    print("GuildRemove : un serveur a supprimé le bot")
    db.removeServeur(guild.id)
    db.removeAllJoueurs(guild.id)
    return


@client.event
async def on_member_remove(member):
    rowCount, res = db.GetJoueurFromMemberId(member.id)
    if rowCount == 1:
        print("MemberRemove : un joueur a quitté un serveur qui a entraîné son retrait de la BDD")
        db.RemoveJoueur(member.guild.id, member.id)
        db.DeleteClassement(res[0][0])
    elif rowCount > 1:
        print("MemberRemove : un joueur a quitté un serveur qui a entraîné son retrait de la BDD")
        db.RemoveJoueur(member.guild.id, member.id)
    return


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    await client.process_commands(message)


@client.tree.command(name="initialize", description="Initialise un nouveau serveur")
async def initialize(ints, channelmessage: discord.TextChannel,
                     roleaping: discord.Role = None):
    print("Initialisation : une initialisation a été demandée")
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
    print("Addjoueur : une demande d'ajout a été envoyée")
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
    print("LeaveLoLWatcher : une demande de retrait a été envoyée")
    rowCount, res = db.GetJoueurFromMemberId(ints.user.id)
    if rowCount == 1:
        db.DeleteClassement(res[0][0])
    exist = False
    for joueur in res:
        if joueur[5] == ints.guild_id:
            exist = True
    if exist:
        db.RemoveJoueur(ints.guild_id, ints.user.id)
        await ints.response.send_message("Vous avez été retiré de la liste")
    else:
        await ints.response.send_message("Vous n'êtes pas présent dans la liste")


@client.tree.command(name="listejoueurs", description="Liste des joueurs")
async def listeJoueurs(ints):
    await ints.response.defer()
    print("Listejoueurs : une liste a été demandée à la BDD")
    res = db.GetJoueursOfGuild(ints.guild_id)
    g = ints.guild
    retour = "Liste de(s) joueur(s) : \n"
    if not res:
        retour = "La liste des joueurs est vide"
    else:
        for i in res:
            try:
                m = await g.fetch_member(i[8])
                retour += " - " + i[1] + " (" + m.name + ") \n"
            except discord.NotFound:
                retour += " - " + i[1] + " (ERREUR : NOT FOUND) \n"
        temp = retour.rsplit('\n', 1)
        retour = ''.join(temp)
    await ints.followup.send(retour)


@client.tree.command(name="infojoueur", description="Donne les infos d'un joueur")
async def info_joueur(ints, summonername: str):
    await ints.response.defer()
    print("Infojoueur : une info de joueur a été demandée à la BDD")
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
    print("Infojoueurdiscord : une info de membre Discord a été demandée à la BDD")
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
    print("Alert : une alerte a été envoyée aux serveurs")
    await ints.followup.send("L'alerte a bien été envoyée")


@client.tree.command(name="alertspeguild", description="Alerte une guilde spécifique en passant par son owner")
async def alertSpeGuild(ints, id_guild: str, message: str):
    if ints.user.id != admin_atlas_id:
        await ints.response.send_message("Seul l'administrateur peut utiliser cette commande")
        return
    await ints.response.defer()
    g = client.get_guild(int(id_guild))
    infos = db.GetServInfoByID(int(id_guild))
    try:
        chan = g.get_channel(int(infos[2]))
        await chan.send("Message de l'admin : \n>>> " + message)
        await ints.followup.send("L'alerte a bien été envoyée dans le salon")
    except discord.errors.Forbidden:
        print("Error : Le bot n'a pas le droit d'envoyer un DM dans le salon. Tentative d'envoi au owner...")
        try:
            await g.owner.send("Message de l'admin : \n>>> " + message)
            await ints.followup.send("L'alerte a bien été envoyée au owner")
        except discord.errors.Forbidden:
            await ints.followup.send("Le bot n'a pas le droit d'envoyer un DM ni au salon ni au owner")


@client.tree.command(name="alertadmin", description="Alerte l'administrateur d'un(e) potentiel(le) problème/demande")
async def alert_admin(ints, message: str):
    await ints.response.defer()
    atlas = await client.fetch_user(admin_atlas_id)
    ret = "<@" + str(ints.user.id) + "> vous a envoyé un message : \n\n" + message
    await atlas.send(ret)
    await ints.followup.send("Votre message a bien été envoyé. Vous serez recontacté sous peu."
                             " Merci de ne pas spam la commande")


@tasks.loop(minutes=3.0)
async def on_update():
    global compteur
    compteur += 1
    print("\nVérification n°" + str(compteur))
    for i in db.UpdatePlayerRecover():
        channel = client.get_channel(i[9])
        if channel is not None:
            guild_infos = [i[7], i[8], i[9], i[10]]
            retour = check_rang(i, guild_infos)
            if retour is None:
                print("Erreur RIOT API.")
            elif retour[0] != "RAS":
                retour[0] += "\n" + displayInfo(retour[1])
                try:
                    await channel.send(str(retour[0]))
                except discord.errors.Forbidden as e:
                    print("Error guild '" + guild_infos[1] + "' : Le bot n'a pas le droit d'écrire"
                                                             " dans le channel initialisé.")
                    print(e)
                    await client.get_guild(int(i[7])).owner.send("Le bot n'a pas le droit d'écrire dans le channel "
                                                                 "initialisé. Veuillez vérifier les permissions "
                                                                 "accordées au bot.")
    print("Fin de la Vérification")

@tasks.loop(time=datetime.time(21, 0, 0, 0, ZoneInfo("Europe/Paris")))
async def classement():
    td = datetime.datetime.now(ZoneInfo("Europe/Paris"))
    if td.weekday() != 6:
        return
    c = db.GetClassement(stratacademy_id)
    msg_return = "La semaine est finie ! Voici les meilleurs joueurs de la semaine : \n"
    msg_return += ":first_place: " + c[0][0] + " (<@" + str(c[0][1]) + ">) avec " + str(c[0][2]) + " victoires !\n"
    msg_return += ":second_place: " + c[1][0] + " (<@" + str(c[1][1]) + ">) avec " + str(c[1][2]) + " victoires !\n"
    msg_return += ":third_place: " + c[2][0] + " (<@" + str(c[2][1]) + ">) avec " + str(c[2][2]) + " victoires !\n"
    msg_return += "\nBravo à tous les participants. La classement est maintenant reset. A la semaine prochaine !"
    await client.get_channel(c[0][3]).send(msg_return)
    db.ResetClassement()


client.run(TOKEN)

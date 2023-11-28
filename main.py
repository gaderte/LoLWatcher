import discord
import requests
from discord.ext import tasks, commands

from Database import Database

compteur = 0

riot_api_key = "X"
atlas_id = 114372984604590080
db = Database()

url_icon_champion = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{0}.png"
url_summoner = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{0}?api_key={1}"  # Récupération EncryptedID + PUUID
url_leaguev4 = "https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{0}?api_key={1}"  # Récupération Elo
url_historique = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{0}/ids?queue=420&start=0&count=1&api_key={1}"  # Récupération historique game
url_resume_match = "https://europe.api.riotgames.com/lol/match/v5/matches/{0}?api_key={1}"  # Récupération données du match

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


def add_player(summoner_name, guild_id, member_id):
    r = requests.get(url_summoner.format(summoner_name, riot_api_key))
    if r.status_code != 200:
        print("Riot Api ERROR - SummonerAPI - Code Erreur : {0}".format(r.status_code))
        return None
    account = r.json()
    r2 = requests.get(url_leaguev4.format(account.get('id'), riot_api_key))
    if r2.status_code != 200:
        print("Riot Api ERROR - LeagueV4API - Code Erreur : {0}".format(r.status_code))
        return None
    # Récupération rank
    rank = r2.json()
    for typegame in rank:
        if typegame.get('queueType') == "RANKED_SOLO_5x5":
            r3 = requests.get(url_historique.format(account.get("puuid"), riot_api_key))
            last_game_played = r3.json()[0]
            rc = db.addJoueur(account.get('id'), account.get('puuid'), account.get('name'), typegame.get('tier'),
                              typegame.get('rank'), typegame.get('leaguePoints'), last_game_played, guild_id, member_id)
            return rc
    return None


def check_last_game(dbinfos):
    r = requests.get(url_historique.format(dbinfos[1], riot_api_key))
    if r.json()[0] != dbinfos[6]:
        return r.json()[0]
    return 0


def check_rang(pinfos, game_id):
    r = requests.get(url_leaguev4.format(pinfos[0], riot_api_key))
    ranking = r.json()
    if r.status_code != 200:
        print("Riot Api ERROR - LeagueV4API - Code Erreur : {0}".format(r.status_code))
        return None, None, None
    for typequeue in ranking:
        if typequeue.get('queueType') == 'RANKED_SOLO_5x5':
            retourFct = ""
            if typequeue.get('tier') == pinfos[3] and typequeue.get('rank') == pinfos[4] and \
                    typequeue.get('leaguePoints') == pinfos[5]:
                db.updateMatchID(pinfos[7], pinfos[8], game_id)
                return None, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('tier') != pinfos[3] \
                    and tiers.get(typequeue.get('tier')) < tiers.get(pinfos[3]):
                retourFct += "de perdre une SoloQ. Il a derank {0} ({1} {2} {3} LP)".format(typequeue.get('tier'), typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('tier') != pinfos[3] \
                    and tiers.get(typequeue.get('tier')) > tiers.get(pinfos[3]):
                retourFct += "de gagner une SoloQ. Il a rank up {0} ({1} {2} {3} LP)".format(typequeue.get('tier'), typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('rank') != pinfos[4] \
                    and ranks.get(typequeue.get('rank')) < ranks.get(pinfos[4]):
                retourFct += "de perdre une SoloQ. Il a derank {0} {1} ({2} {3} {4} LP)".format(typequeue.get('tier'), typequeue.get('rank'), typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('rank') != pinfos[4] \
                    and ranks.get(typequeue.get('rank')) > ranks.get(pinfos[4]):
                retourFct += "de gagner une SoloQ. Il a rank up {0} {1} ({2} {3} {4} LP)".format(typequeue.get('tier'), typequeue.get('rank'), typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('leaguePoints') != pinfos[5] \
                    and typequeue.get('leaguePoints') < pinfos[5]:
                retourFct += "de perdre une SoloQ. Il a perdu {0} LPs ({1} {2} {3} LP)".format(int(typequeue.get('leaguePoints')) - pinfos[5], typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")
            if typequeue.get('leaguePoints') != pinfos[5] \
                    and typequeue.get('leaguePoints') > pinfos[5]:
                retourFct += "de gagner une SoloQ. Il a gagné {0} LPs ({1} {2} {3} LP)".format(int(typequeue.get('leaguePoints')) - pinfos[5], typequeue.get('tier'), typequeue.get('rank'), typequeue.get('leaguePoints'))
                db.updateJoueur(pinfos[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), game_id, pinfos[7])
                return retourFct, typequeue.get("wins"), typequeue.get("losses")


def create_embed(pinfos, descriptif, i, wins, losses):
    if pinfos[7].nick:
        n = pinfos[7].nick
    else:
        n = pinfos[7].name
    if pinfos[6]:
        if descriptif is None:
            embed = discord.Embed(title="Victoire", description="{0} est actuellement {1} {2} {3} LP".format(n, i[3], i[4], i[5]),
                                  color=0x00ff00)
        else:
            embed = discord.Embed(title="Victoire", description="{0} vient {1}".format(n, descriptif),
                                  color=0x00ff00)
    else:
        if descriptif is None:
            embed = discord.Embed(title="Défaite", description="{0} est actuellement {1} {2} {3} LP".format(n, i[3], i[4], i[5]),
                                  color=0xff0000)
        else:
            embed = discord.Embed(title="Défaite", description="{0} vient {1}".format(n, descriptif),
                                  color=0xff0000)

    embed.set_author(name="LoLWatcher - Résumé de la partie")
    embed.set_thumbnail(url=url_icon_champion.format(pinfos[1]))
    embed.add_field(name="Score", value="{0}/{1}/{2}".format(pinfos[3], pinfos[4], pinfos[5]), inline=True)
    embed.add_field(name="Champion", value=pinfos[0], inline=True)
    embed.add_field(name="Role", value=pinfos[2], inline=True)
    if wins is not None and losses is not None:
        embed.add_field(name="WinRate", value="{0}%".format(round(int(wins) * 100/(int(wins) + int(losses)), 2)), inline=True)

    return embed


@client.event
async def on_ready():
    print("Connecté en tant que : {0} ({1})".format(client.user.name, client.user.id))
    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(
            f'{guild.name}(id: {guild.id})'
        )
    print("Synchro du tree...")
    await client.tree.sync()
    await client.wait_until_ready()
    on_update.start()


@client.event
async def on_guild_join(guild):
    print("Le bot a été ajouté sur un serveur")
    db.addServeur(guild.id, guild.name, 0, 0)
    return


@client.event
async def on_guild_remove(guild):
    print("Le bot a quitté une guilde")
    db.removeServeur(guild.id)
    db.removeAllJoueurs(guild.id)
    return


@client.event
async def on_member_remove(member):
    rowcount = db.deleteJoueurByMemberID(member.id, member.guild.id)
    if rowcount == 1:
        print("MemberRemove : un joueur a quitté un serveur qui a entraîné son retrait de la BDD")
    return


@client.tree.command(name="initialize", description="Initialise les informations du serveur")
async def initialize(ints, channelmessage: discord.TextChannel, roleaping: discord.Role = None):
    print("Une demande d'initialisation a été envoyée")
    await ints.response.defer()
    try:
        msg = "Message test. Si vous voyez ce message, cela signifie que le bot a l'autorisation d'écrire dans le channel."
        msg_retour = await channelmessage.send(msg)
        await msg_retour.delete()
    except discord.errors.Forbidden:
        msg = "Le bot n'a pas l'autorisation d'écrire dans le channel : " + channelmessage.name + \
              ". Veuillez changer de channel ou accorder les autorisations avant de recommencer."
        await ints.response.send_message(msg)
        return
    else:
        if not roleaping:
            db.initializeServer(ints.guild_id, channelmessage.id, 0)
        else:
            db.initializeServer(ints.guild_id, channelmessage.id, roleaping.id)
        await ints.followup.send("Le serveur a bien été initialisé.")


@client.tree.command(name="alertspeguild", description="Alerte une guilde spécifique en passant par son owner")
async def alertSpeGuild(ints, id_guild: str, message: str):
    if ints.user.id != atlas_id:
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
    atlas = await client.fetch_user(atlas_id)
    ret = "<@" + str(ints.user.id) + "> vous a envoyé un message : \n\n" + message
    await atlas.send(ret)
    await ints.followup.send("Votre message a bien été envoyé. Vous serez recontacté sous peu."
                             " Merci de ne pas spam la commande")


@client.tree.command(name="alert", description="Alerte tous les utilisateurs du bot")
async def alertGuilds(ints, message: str):
    if ints.user.id != atlas_id:
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
                retour += " - " + i[2] + " (" + m.name + ") \n"
            except discord.NotFound:
                retour += " - " + i[2] + " (ERREUR : NOT FOUND) \n"
        temp = retour.rsplit('\n', 1)
        retour = ''.join(temp)
    await ints.followup.send(retour)


@client.tree.command(name="ajoutjoueur", description="Ajoute un joueur à la base de données")
async def add_joueur(ints, summoner_name: str):
    print("Une demande d'ajout a été envoyée")
    player = add_player(summoner_name, ints.guild_id, ints.user.id)
    if not player:
        await ints.response.send_message("Erreur lors de l'ajout du joueur. Veuillez vérifier le summoner name.")
    elif player == 1:
        await ints.response.send_message("Vous avez bien été ajouté au bot")
    else:
        await ints.response.send_message("Vous êtes déjà dans la liste du bot")


@client.tree.command(name="retraitjoueur", description="Sortir de la liste LoLWatcher")
async def remove_joueur(ints):
    print("Une demande de retrait a été effectuée")
    rc = db.deleteJoueurByMemberID(ints.user.id, ints.guild_id)
    if rc == 1:
        await ints.response.send_message("Vous avez été retiré du bot LoLWatcher")
    else:
        await ints.response.send_message("Vous n'êtes pas présent dans la base de données")


@tasks.loop(minutes=2, seconds=30)
async def on_update():
    global compteur
    compteur += 1
    print("Vérification n°{0}".format(compteur))
    for i in db.UpdatePlayerRecover(compteur):
        channel = client.get_channel(i[11])
        if channel is not None:
            gameID = check_last_game(i)
            if gameID != 0:
                r = requests.get(url_resume_match.format(gameID, riot_api_key))
                participants = r.json().get('info').get('participants')
                for player in participants:
                    if player.get('puuid') == i[1]:
                        member = await client.get_guild(i[7]).fetch_member(i[8])
                        p_info = [player.get('championName'), player.get('championId'), player.get('lane'), player.get('kills'),
                                  player.get('deaths'), player.get('assists'), player.get('win'), member]
                        retour, wins, losses = check_rang(i, gameID)
                        try:
                            if i[12] != 0:
                                role = client.get_guild(i[7]).get_role(i[12])
                                await channel.send(content=role.mention, embed=create_embed(p_info, retour, i, wins, losses))
                            else:
                                await channel.send(embed=create_embed(p_info, retour, i, wins, losses))
                        except discord.errors.Forbidden as e:
                            print("Error guild '" + p_info[10] + "' : Le bot n'a pas le droit d'écrire dans le channel initialisé.")
                            print(e)
                            await client.get_guild(int(i[7])).owner.send(
                                "Le bot n'a pas le droit d'écrire dans le channel "
                                "initialisé. Veuillez vérifier les permissions accordées au bot."
                            )
    print("Fin de la vérification")


client.run("X")

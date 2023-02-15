import mysql.connector

class Database(object):
    connection_params = {
        'host': "X",
        'user': "X",
        'password': "X",
        'database': "X"
    }

    def InitializeServer(self, guildid, cim, rtp):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "UPDATE serveurs SET channelIdMessage=%s, roleToPing=%s " \
                          "WHERE guildId=%s"
                params = [cim, rtp, guildid]
                c.execute(request, params)
                db.commit()

    def addServeur(self, guildid, guildname, cim, rtp):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "INSERT INTO serveurs (guildID, guildName, channelIdMessage, roleToPing) "\
                       "VALUES (%s, %s, %s, %s)"
                params = [guildid, guildname, cim, rtp]
                c.execute(request, params)
                db.commit()

    def removeServeur(self, guildid):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "DELETE FROM serveurs WHERE guildID=%s ;"
                params = [guildid]
                c.execute(request, params)
                db.commit()

    def removeAllJoueurs(self, guildid):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "DELETE FROM joueurs WHERE guildID=%s ;"
                params = [guildid]
                c.execute(request, params)
                db.commit()

    def addJoueur(self, encryptedid, summonername, tier, rank, lps, eb, prog, guildid, member_id):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "INSERT INTO joueurs (EncryptedID, SummonerName, Tier, Rank, leaguePoints, enBO, Progress, " \
                          "guildID, memberID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                params = [encryptedid, summonername, tier, rank, lps, eb, prog, guildid, member_id]
                try:
                    c.execute(request, params)
                    db.commit()
                    return c.rowcount
                except mysql.connector.errors.IntegrityError:
                    return 2

    def RemoveJoueur(self, guildid, member_id):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "DELETE FROM joueurs WHERE guildID=%s AND memberID=%s"
                params = [guildid, member_id]
                c.execute(request, params)
                db.commit()
                return c.rowcount

    def recoverSpecificJoueur(self, idjoueur, guildid):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor(buffered=True) as c:
                request = "SELECT * FROM joueurs WHERE EncryptedID=%s AND guildID=%s;"
                params = [idjoueur, guildid]
                c.execute(request, params)
                resultats = c.fetchone()
                return resultats

    def updateJoueur(self, playerid, summonername, tier, rank, lps, eb, prog):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "UPDATE joueurs SET SummonerName=%s, Tier=%s, Rank=%s, leaguePoints=%s, enBO=%s, Progress=%s"\
                          " WHERE EncryptedID=%s"
                params = [summonername, tier, rank, lps, eb, prog, playerid]
                c.execute(request, params)
                db.commit()

    def recoverAllGuilds(self):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "SELECT * FROM serveurs WHERE channelIdMessage != 0"
                c.execute(request)
                results = c.fetchall()
                return results

    def GetJoueursOfGuild(self, guildid):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                request = "SELECT * FROM joueurs WHERE guildID=" + str(guildid) + ";"
                c.execute(request)
                resultats = c.fetchall()
                return resultats

    def GetPlayerInfo(self, guildid, summonername):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor(buffered=True) as c:
                request = "SELECT * FROM joueurs WHERE guildID=%s and SummonerName=%s"
                params = [guildid, summonername]
                c.execute(request, params)
                result = c.fetchone()
                return result

    def GetPlayerInfoDiscord(self, guildid, discordid):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor(buffered=True) as c:
                request = "SELECT * FROM joueurs WHERE guildID=%s and memberID=%s"
                params = [guildid, discordid]
                c.execute(request, params)
                result = c.fetchone()
                return result


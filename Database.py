import mysql.connector

class Database:

    def __init__(self):
        try:
            self.db = mysql.connector.connect(host="X",
                                              user="X",
                                              password="X",
                                              database="X")
            self.cursor = self.db.cursor(buffered=True)
        except Exception as e:
            print(e)

    def addServeur(self, guildid, guildname, cim, rtp):
        request = "INSERT INTO serveurs (guildID, guildName, channelIdMessage, roleToPing) " \
                  "VALUES (%s, %s, %s, %s)"
        params = [guildid, guildname, cim, rtp]
        self.cursor.execute(request, params)
        self.db.commit()

    def initializeServer(self, guildid, cim, rtp):
        request = "UPDATE serveurs SET channelIdMessage=%s, roleToPing=%s " \
                  "WHERE guildId=%s"
        params = [cim, rtp, guildid]
        self.cursor.execute(request, params)
        self.db.commit()

    def removeServeur(self, guildid):
        request = "DELETE FROM serveurs WHERE guildID=%s ;"
        params = [guildid]
        self.cursor.execute(request, params)
        self.db.commit()

    def addJoueur(self, encryptedid, puuid, summonername, tier, rank, lps, lgp, guildid, member_id):
        request = "INSERT INTO joueurs (EncryptedID, puuid, SummonerName, Tier, Rank, leaguePoints, lastgameplayed, " \
                  "guildID, memberID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = [encryptedid, puuid, summonername, tier, rank, lps, lgp, guildid, member_id]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.errors.IntegrityError:
            return 2

    def deleteJoueurByMemberID(self, member_id, guild_id):
        request = "DELETE FROM joueurs WHERE memberID=%s AND guildID=%s"
        params = [member_id, guild_id]
        self.cursor.execute(request, params)
        self.db.commit()
        return self.cursor.rowcount

    def UpdatePlayerRecover(self, compteur):
        request = "SELECT * FROM joueurs, serveurs WHERE joueurs.guildID = serveurs.guildID ORDER BY " \
                  "joueurs.EncryptedID "
        if compteur % 2 == 0:
            request += "DESC LIMIT 80"
        else:
            request += "ASC LIMIT 80"
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return result

    def GetServInfoByID(self, guildid):
        request = "SELECT * FROM serveurs WHERE guildID = %s"
        params = [guildid]
        self.cursor.execute(request, params)
        return self.cursor.fetchone()

    def recoverAllGuilds(self):
        request = "SELECT * FROM serveurs WHERE channelIdMessage != 0"
        self.cursor.execute(request)
        results = self.cursor.fetchall()
        return results

    def GetJoueursOfGuild(self, guildid):
        request = "SELECT * FROM joueurs WHERE guildID=" + str(guildid) + ";"
        self.cursor.execute(request)
        resultats = self.cursor.fetchall()
        return resultats

    def GetJoueurFromMemberId(self, memberID):
        request = "SELECT * FROM joueurs WHERE memberID = %s"
        params = [memberID]
        self.cursor.execute(request, params)
        return self.cursor.rowcount, self.cursor.fetchall()

    def RemoveJoueur(self, guildid, member_id):
        request = "DELETE FROM joueurs WHERE guildID=%s AND memberID=%s"
        params = [guildid, member_id]
        self.cursor.execute(request, params)
        self.db.commit()

    def removeAllJoueurs(self, guildid):
        request = "DELETE FROM joueurs WHERE guildID=%s"
        params = [guildid]
        self.cursor.execute(request, params)
        self.db.commit()

    def updateMatchID(self, guildid, memberid, gameid):
        request = "UPDATE joueurs SET lastgameplayed=%s WHERE guildID=%s AND memberID=%s"
        params = [gameid, guildid, memberid]
        self.cursor.execute(request, params)
        self.db.commit()

    def updateJoueur(self, playerid, summonername, tier, rank, lps, gameid, guildid):
        request = "UPDATE joueurs SET SummonerName=%s, Tier=%s, Rank=%s, leaguePoints=%s, lastgameplayed=%s"\
                  " WHERE EncryptedID=%s AND guildID=%s"
        params = [summonername, tier, rank, lps, gameid, playerid, guildid]
        self.cursor.execute(request, params)
        self.db.commit()

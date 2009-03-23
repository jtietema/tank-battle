from hulknet.server.game import ServerGame

class TankBattleGame(ServerGame):
    def __init__(self, application):
        ServerGame.__init__(self,application)
        self.players = []
    
    def addPlayer(self, player):
        self.players.append(player)
        player.currentGame = self
        return 1
    
    def removePlayer(self, player):
        self.players.remove(player)
        
        for p in self.players:
            p.protocol.sendPlayerLeave(player.name)

    def update(self, interval):
        pass
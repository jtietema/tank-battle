from hulknet.client.factory import GameClientFactory

class TankBattleClientFactory(GameClientFactory):
    def buildProtocol(self, addr):
        print 'Connected'
        return TankBattleClientProtocol(self.app)
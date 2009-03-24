from hulknet.client.factory import GameClientFactory
from tank_battle.client.protocol import TankBattleClientProtocol

class TankBattleClientFactory(GameClientFactory):
    def buildProtocol(self, addr):
        print 'Connected'
        return TankBattleClientProtocol(self.app)
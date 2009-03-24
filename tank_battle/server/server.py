from hulknet.server.gameserver import GameServerApp
from tank_battle.server.protocol import TankBattleServerProtocol
from tank_battle.server.game import TankBattleGame

class TankBattleServer(GameServerApp):
    def __init__(self, port):
        GameServerApp.__init__(self, port, TankBattleServerProtocol, TankBattleGame(self))
    
    def tankState(self, id, rot, (x,y)):
        print "TANKID#"+str(id)+' '+str(rot)+' ('+str(x)+','+str(y)+')'
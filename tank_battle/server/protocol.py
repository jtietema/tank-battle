from hulknet.server.protocol import ServerProtocol
from tank_battle.common.messages import *

class TankBattleServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)
        
        # register handles
        self.registerHandler(CS_TANK_STATE, self.onTankState)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        print "TANKID#"+str(id)+' '+str(rot)+' ('+str(x)+','+str(y)+')'
        
        return True
        # TODO call function on app
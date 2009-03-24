import xdrlib

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
        self.app.clientTankState(id, rot, (x,y))
        return True
        
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        
        packer.pack_int(SC_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)
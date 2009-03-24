import xdrlib

from hulknet.server.protocol import ServerProtocol
from tank_battle.common.messages import *

class TankBattleServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)
        # send a tank ID to the player
        self.app.tankId(player)
        # register handles
        self.registerHandler(CS_TANK_STATE, self.onTankState)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        print "TANKID#"+str(id)+' '+str(rot)+' ('+str(x)+','+str(y)+')'
        return self.app.tankState(id, rot, (x,y), self.player)
        
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        
        packer.pack_int(SC_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_float(x)
        packer.pack_float(y)
        self.writePacker(packer)
    
    def sendTankId(self, id):
        packer = xdrlib.Packer()
        packer.pack_int(SC_TANK_ID)
        packer.pack_int(id)
        self.writePacker(packer)
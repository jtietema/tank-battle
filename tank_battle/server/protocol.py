import xdrlib

from hulknet.server.protocol import ServerProtocol
from tank_battle.common.messages import *

class TankBattleServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)
        # send a tank ID to the player
        self.tank_id = None
        self.app.tankId(self.player)
        # register handles
        self.registerHandler(CS_TANK_STATE, self.onTankState)
        self.registerHandler(CS_TANK_ID, self.onTankId)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        print "TANKID#"+str(id)+' '+str(rot)+' ('+str(x)+','+str(y)+')'
        return self.app.tankState(id, rot, (x,y), self.player)
    
    def onTankId(self, unpacker):
        return self.app.tankId(self.player)
    
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        
        packer.pack_int(SC_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_float(x)
        packer.pack_float(y)
        self.writePacker(packer)
    
    def sendTankId(self, id):
        self.tank_id = id
        packer = xdrlib.Packer()
        packer.pack_int(SC_TANK_ID)
        packer.pack_int(id)
        self.writePacker(packer)
    
    def connectionLost(self, reason):
        ServerProtocol.connectionLost(self, reason)
        self.app.tankRemove(self.tank_id)
    
    def sendTankRemove(self, id):
        packer = xdrlib.Packer()
        packer.pack_int(SC_TANK_REMOVE)
        packer.pack_int(id)
        self.writePacker(packer)
    
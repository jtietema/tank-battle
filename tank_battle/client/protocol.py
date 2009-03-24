import xdrlib

from hulknet.client.protocol import ClientProtocol
from tank_battle.common.messages import *

class TankBattleClientProtocol(ClientProtocol):
    
    def connectionMade(self):
        print 'connection made...'
        ClientProtocol.connectionMade(self)
        # register custom handlers below
        self.registerHandler(SC_TANK_STATE, self.onTankState)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        self.app.serverTankState(id,rot,(x,y))
        return True
    
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        
        packer.pack_int(CS_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)
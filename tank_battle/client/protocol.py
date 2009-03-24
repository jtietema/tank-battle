import xdrlib

from hulknet.client.protocol import ClientProtocol
from tank_battle.common.messages import *

class TankBattleClientProtocol(ClientProtocol):
    
    def connectionMade(self):
        print 'connection made...'
        ClientProtocol.connectionMade(self)
        # register custom handlers below
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        x = unpacker.unpack_int()
        y = unpacker.unpack_int()
        #self.app.serverTankState(id,rot,(x,y))
    
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        packer.pack_int(CS_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_int(x)
        packer.pack_int(y)
        self.writePacker(packer)
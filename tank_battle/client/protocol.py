import xdrlib

from hulknet.client.protocol import ClientProtocol
from tank_battle.common.messages import *

class TankBattkeClientProtocol(ClientProtocol):
    
    def connectionMade(self):
        print 'connection made...'
        ClienProtocol.connectionMade(self)
        # register custom handlers below
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_int()
        x = unpacker.unpack_int()
        y = unpacker.unpack_int()
        #self.app.serverTankState(id,rot,(x,y))
    
    def sendTankState(self,id,rot,(x,y)):
        packer = xdrlib.Packer()
        packer.pack_int(CS_TANK_STATE)
        packer.pack_int(id)
        packer.pack_int(rot)
        packer.pack_int(x)
        packer.pack_int(y)
        self.writePacker(packer)
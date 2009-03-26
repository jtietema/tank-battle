from hulknet.common.packer import Packer
from hulknet.client.protocol import ClientProtocol
from tank_battle.common.messages import *

class TankBattleClientProtocol(ClientProtocol):
    
    def connectionMade(self):
        print 'connection made...'
        ClientProtocol.connectionMade(self)
        # register custom handlers below
        self.registerHandler(SC_TANK_STATE, self.onTankState)
        self.registerHandler(SC_TANK_ID, self.onTankID)
        self.registerHandler(SC_TANK_REMOVE, self.onTankRemove)
        self.registerHandler(SC_FIRE, self.onFire)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        rot_signum = unpacker.unpack_int()
        speed = unpacker.unpack_float()
        driving_signum = unpacker.unpack_int()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        self.app.serverTankState(id, rot, rot_signum, speed, driving_signum, (x, y))
        return True
    
    def onTankID(self, unpacker):
        id = unpacker.unpack_int()
        
        print "[->] TANK_ID #%d" % (id,)
        
        self.app.serverTankID(id)
        return True
    
    def onTankRemove(self, unpacker):
        id = unpacker.unpack_int()
        
        print "[->] REMOVE_TANK #%d" % (id,)
        
        self.app.serverTankRemove(id)
        return True
    
    def onFire(self, unpacker):
        """Called when the server validates a shot."""
        bullet_id = unpacker.unpack_int()
        rotation = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        
        print "[<-] FIRE #%d <rotation:%f, location:(%f, %f)>" % (bullet_id, rotation, x, y)
        
        self.app.serverFire(bullet_id, rotation, (x, y))
        
        return True
    
    def sendTankState(self, id, rot, rot_signum, speed, driving_signum, (x,y)):        
        packer = Packer()
        
        packer.pack_int(CS_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_int(rot_signum)
        packer.pack_float(speed)
        packer.pack_int(driving_signum)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)
    
    def sendTankId(self):
        packer = Packer()
        packer.pack_int(CS_TANK_ID)        
        self.writePacker(packer)
    
    def sendFire(self, tank_id, rotation, (x, y)):
        print "[->] REQUEST_FIRE <rotation:%f, location:(%f, %f)>" % (rotation, x, y)
        
        packer = Packer()
        packer.pack_int(CS_REQUEST_FIRE)
        packer.pack_int(tank_id)
        packer.pack_float(rotation)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)

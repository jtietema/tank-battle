from hulknet.common.packer import Packer
from hulknet.server.protocol import ServerProtocol
from tank_battle.common.messages import *

class TankBattleServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)
        
        print "[<-] REQUEST_TANK_ID"
        
        # send a tank ID to the player
        self.tank_ids = []
        self.app.tankId(self.player)
        
        # register handles
        self.registerHandler(CS_TANK_STATE, self.onTankState)
        self.registerHandler(CS_TANK_ID, self.onTankId)
        self.registerHandler(CS_REQUEST_FIRE, self.onFire)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_float()
        rot_signum = unpacker.unpack_int()
        speed = unpacker.unpack_float()
        driving_signum = unpacker.unpack_int()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        print "[<-] TANK_STATE #%d <rotation:%f, rotation_signum:%d, speed:%f, driving_signum:%d, position:(%f, %f)>" % (id, rot, rot_signum, speed, driving_signum, x, y)
        
        self.app.tankState(id, rot, rot_signum, speed, driving_signum, (x,y), self.player)
        
        return True
        
    def onTankId(self, unpacker):
        return self.app.tankId(self.player)
    
    def onFire(self, unpacker):
        tank_id = unpacker.unpack_int()
        rotation = unpacker.unpack_float()
        x = unpacker.unpack_float()
        y = unpacker.unpack_float()
        
        self.app.fire(tank_id, rotation, (x, y))
        
        return True
    
    def sendTankState(self, id, rot, rot_signum, speed, driving_signum, (x, y)):
        packer = Packer()
        
        packer.pack_int(SC_TANK_STATE)
        packer.pack_int(id)
        packer.pack_float(rot)
        packer.pack_int(rot_signum)
        packer.pack_float(speed)
        packer.pack_int(driving_signum)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)
    
    def sendTankId(self, id):
        self.tank_ids.append(id)
        
        print "[->] TANK_ID #%d" % (id,)
        
        packer = Packer()
        packer.pack_int(SC_TANK_ID)
        packer.pack_int(id)
        self.writePacker(packer)
    
    def connectionLost(self, reason):
        ServerProtocol.connectionLost(self, reason)
        
        for id in self.tank_ids:
            print "[<-] REMOVE_TANK #%d" % (id,)
            self.app.tankRemove(id)
    
    def sendTankRemove(self, id):
        packer = Packer()
        
        print "[->] REMOVE_TANK #%d" % (id,)
        
        packer.pack_int(SC_TANK_REMOVE)
        packer.pack_int(id)
        self.writePacker(packer)
    
    def sendFire(self, bullet_id, rotation, (x, y)):
        packer = Packer()
        
        print "[->] FIRE <rotation:%f, location(%f,%f)>" % (rotation, x, y)
        
        packer.pack_int(SC_FIRE)
        packer.pack_int(bullet_id)
        packer.pack_float(rotation)
        packer.pack_float(x)
        packer.pack_float(y)
        
        self.writePacker(packer)
        

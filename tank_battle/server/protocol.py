from hulknet.server.protocol import ServerProtocol

class TankBattleServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)
        
        # register handles
        self.registerHandler(CS_TANK_STATE, self.onTankState)
    
    def onTankState(self,unpacker):
        id = unpacker.unpack_int()
        rot = unpacker.unpack_int()
        x = unpacker.unpack_int()
        y = unpacker.unpack_int()
        print "TANKID#"+str(id)+' '+str(rot)+' ('+str(x)+','+str(y)+')'
        # TODO call function on app
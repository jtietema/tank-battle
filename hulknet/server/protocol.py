from hulknet.common.packer import Packer
from hulknet.common.gprotocol import GProtocol
from hulknet.common.messages import *

class ServerProtocol(GProtocol):
    """Server side version of the game protocol.
    """
    def __init__(self, app):
        self.app = app
    
    def connectionMade(self):
        """Create a player for this connection
        """
        GProtocol.connectionMade(self)
        self.player = self.app.addPlayer(self)
        
        # setup message handlers
        self.registerHandler(CS_HELLO, self.onHello)
    
    def connectionLost(self, reason):
        """Remove the player from the game.
        """
        self.app.removePlayer(self.player)
    
    def onHello(self, unpacker):
        name = unpacker.unpack_string()
        return self.app.hello(name, self.player)
    
    def sendPlayerLeave(self, playerName):
        packer = Packer()
        packer.pack_int(SC_PLAYER_LEAVE)
        packer.pack_string(playerName)
        self.writePacker(packer)
    
    def sendPlayerJoin(self, playerName):
        packer = Packer()
        packer.pack_int(SC_PLAYER_JOIN)
        packer.pack_string(playerName)
        self.writePacker(packer)
    
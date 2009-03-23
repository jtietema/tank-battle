import xdrlib

from hulknet.common.gprotocol import GProtocol
from hulknet.common.messages import *

class ClientProtocol(GProtocol):
    """Client side of GProtocol
    """
    def __init__(self, app):
        self.app = app
    
    def connectionMade(self):
        GProtocol.connectionMade(self)
        
        # setup message handlers
        self.registerHandler(GProtocol.MSG_ERROR, self.onError)
        self.registerHandler(SC_PLAYER_LEAVE, self.onPlayerLeave)
        self.registerHandler(SC_PLAYER_JOIN, self.onPlayerJoin)
        
        self.app.onConnected(self)

    ### Message handler methods ###

    def onError(self, unpacker):
        errorId = unpacker.unpack_int()
        errorMsg = unpacker.unpack_string()
        print "ERROR [%d] %s" % (errorId, errorMsg)
        return 1
        
    def onPlayerLeave(self, unpacker):
        name = unpacker.unpack_string()
        self.app.serverPlayerLeave(name)
        return 1
    
    def onPlayerJoin(self, unpacker):
        name = unpacker.unpack_string()
        self.app.serverPlayerJoin(name)
        
    ### Message sender methods ###

    def sendHello(self, name):
        packer = xdrlib.Packer()
        packer.pack_int(CS_HELLO)
        packer.pack_string(name)
        self.writePacker(packer)
    

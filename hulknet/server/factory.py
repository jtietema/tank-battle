from twisted.internet.protocol import Factory

class GameProtocolFactory(Factory):
    """Factory to pass the game server instance to protocol
    instances when they are created.
    """
    def __init__(self, app, protocolClass):
        # app == gameserver
        self.app = app
        self.protocolClass = protocolClass
    
    def buildProtocol(self, addr):
        """Construct a protocol instance with reference to
        the factory and the gameserver.
        """
        p = self.protocolClass(self.app)
        p.factory = self
        return p
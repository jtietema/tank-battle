
from twisted.internet.protocol import ClientFactory

from protocol import ClientProtocol

class GameClientFactory(ClientFactory):

    def __init__(self, app):
        self.app = app
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
    
    def buildProtocol(self, addr):
        print 'Connected.'
        return ClientProtocol(self.app)
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

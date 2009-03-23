from hulknet.client.protocol import ClientProtocol

class TankBattkeClientProtocol(ClientProtocol):
    
    def connectionMade(self):
        print 'connection made...'
        ClienProtocol.connectionMade(self)
        # register custom handlers below
    
    
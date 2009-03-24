import random
import time

from twisted.internet import reactor

from hulknet.common.player import Player

class GenericClientApp:
    def __init__(self, clientFactoryClass):
        self.clientFactoryClass = clientFactoryClass
        self.playerName = "Player%d" % random.randint(0,1000)
        self.gameNames = []
        self.currentGame = None
        self.player = None

    def update(self, interval):
        """Update the network via the Twisted Reactor.
        """
        reactor.runUntilCurrent()
        reactor.doSelect(0)

    def onConnected(self, protocol):
        self.player = Player(protocol)
        self.requestHello()
        return self.player

    def exit(self):
        self.running = 0

    def connect(self, hostname, port):
        print "Connecting to:", hostname, port
        reactor.connectTCP(hostname, port, self.clientFactoryClass(self))
        reactor.running = 1

    def addPlayer(self, protocol):
        self.player = Player(protocol)
        self.requestConnect()
        return self.player

    def removePlayer(self, player):
        pass

    ### Send Requests To Server ###

    def requestHello(self):
        self.player.protocol.sendHello(self.playerName)


    ### server message handlers ###

    def serverPlayerLeave(self, playerName):
        pass
    
    def serverPlayerJoin(self, playerName):
        pass
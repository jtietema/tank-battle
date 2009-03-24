import time

from twisted.internet import reactor

from factory import GameProtocolFactory
from hulknet.common.player import Player

class GameServerApp:
    """GameServerApp is the central management class of the server.
    Tracks all of the connected players.
    """
    def __init__(self, port, protocolClass, game):
        self.port = port
        self.game = game
        self.factory = GameProtocolFactory(self, protocolClass)
        reactor.listenTCP(port, self.factory)
        self.players = []
        self.running = 1
    
    def run(self, delay):
        """Run the server until the game ends.
        """
        self.lastFrame = time.time()
        self.beginFrame = time.time()
        
        print "Server running."
        while self.running:
            self.iterate()
            time.sleep(delay)
    
    def iterate(self):
        """Execute a single iteration of the server (game loop).
        """
        now = time.time()
        interval = now - self.beginFrame
        self.beginFrame = now
        
        # update the network
        reactor.doSelect(0)
        
        # update the game
        self.game.update(interval)
    
    def hello(self, name, player):
        """Player login message
        """
        player.name = name
        return 1
    
    def addPlayer(self, protocol):
        print "Adding player"
        newPlayer = Player(protocol)
        self.players.append(newPlayer)
        result = self.game.addPlayer(newPlayer)
        if result:
            newPlayer.currentGame = self.game
        return newPlayer
    
    def removePlayer(self, player):
        print "Removing player"
        self.game.removePlayer(player)
        self.players.remove(player)
        player.destroy()
    
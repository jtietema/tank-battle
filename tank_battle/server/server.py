from hulknet.server.gameserver import GameServerApp
from tank_battle.server.protocol import TankBattleServerProtocol
from tank_battle.server.game import TankBattleGame

class TankBattleServer(GameServerApp):    
    def __init__(self, port):
        GameServerApp.__init__(self, port, TankBattleServerProtocol, TankBattleGame(self))
        self.currentId = 0
        self.last_known_states = {}
    
    def tankState(self, id, rot, (x,y), source_player):
        '''Send the message back to all clients'''
        self.last_known_states[id] = (rot, x, y)
        
        for player in self.players:
            if player is not source_player:
                player.protocol.sendTankState(id, rot, (x, y))
    
    def tankId(self, player):
        for id, (rot, x, y) in enumerate(self.last_known_states):
            player.protocol.sendTankState(id, rot, (x, y))
        
        self.currentId += 1
        player.protocol.sendTankId(self.currentId)
    
    def tankRemove(self, id):
        del self.last_known_states[id]
        
        for player in self.players:
            player.protocol.sendTankRemove(id)
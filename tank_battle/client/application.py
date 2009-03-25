from hulknet.client.application import GenericClientApp


from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
from cocos.sprite import Sprite
import cocos.tiles
from tank_battle.tank import Tank, PlayerTank, ComputerTank
import tiled2cocos


class TankBattleClient(GenericClientApp):
    def __init__(self, clientFactoryClass):
        GenericClientApp.__init__(self,clientFactoryClass)
        self.players = {}
        self.tank_layer = None
        self.computer_players = {}
    
    def run(self):
        director.init(caption='Tank Battle', width=800, height=600)

        self.current_map = tiled2cocos.load_map('map2.tmx')

        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        director.window.push_handlers(self.on_key_press)

        self.scroller = cocos.tiles.ScrollingManager()
        
        self.players_layer = cocos.tiles.ScrollableLayer()

        self.scroller.add(self.current_map)
        self.scroller.add(self.players_layer)
        
        scene = Scene(self.scroller)
        
        scene.schedule(self.update)
        
        self.connect('10.9.8.80', 7777)
        
        director.show_FPS = True
        
        director.run(scene)
    
    def update(self, dt):
        GenericClientApp.update(self, dt)
        for tank in self.computer_players:
            tank.update(dt)
    
    def on_key_press(self, k, modifier):
        if k == key.A:
            self.requestTankId()
    
    def requestTankId(self):
        self.player.protocol.sendTankId()
    
    def serverTankID(self, id):
        if not self.tank_layer:
            self.tank_layer = cocos.tiles.ScrollableLayer()
            tank = PlayerTank(id, ((self.current_map.px_width // 2), (self.current_map.px_height // 2)), self)
            self.tank_layer.add(tank)
            self.scroller.add(self.tank_layer)
        else:
            ai_tank = ComputerTank(id, ((self.current_map.px_width // 2), (self.current_map.px_height // 2)), self)
            self.tank_layer.add(ai_tank)
    
    def serverTankRemove(self, id):
        self.players_layer.remove(self.players[id])
        del self.players[id]
    
    def serverTankState(self, id, rot, (x,y)):
        if id not in self.players:
            self.players[id] = Tank(id, (x, y))
            self.players_layer.add(self.players[id])
        self.players[id].rotation = rot
        self.players[id].x = x
        self.players[id].y = y
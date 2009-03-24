from hulknet.client.application import GenericClientApp


from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
from cocos.sprite import Sprite
import cocos.tiles
from tank_battle.tank import Tank, PlayerTank
import tiled2cocos


class TankBattleClient(GenericClientApp):
    def __init__(self, clientFactoryClass):
        GenericClientApp.__init__(self,clientFactoryClass)
        self.players = {}
    
    def run(self):        
        director.init(caption='Tank Battle', width=800, height=600)

        self.current_map = tiled2cocos.load_map('map2.tmx')

        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)

        self.scroller = cocos.tiles.ScrollingManager()
        
        self.players_layer = cocos.tiles.ScrollableLayer()

        self.scroller.add(self.current_map)
        self.scroller.add(self.players_layer)
        
        scene = Scene(self.scroller)
        
        scene.schedule(self.update)
        
        self.connect('10.9.8.80', 7777)
        
        director.run(scene)
    
    def serverTankID(self, id):
        tank_layer = cocos.tiles.ScrollableLayer()
        tank = PlayerTank(id, ((self.current_map.px_width // 2), (self.current_map.px_height // 2)), self)
        tank_layer.add(tank)
        
        self.scroller.add(tank_layer)
    
    def serverTankRemove(self, id):
        del self.players[id]
    
    def serverTankState(self, id, rot, (x,y)):
        if id not in self.players:
            self.players[id] = Tank(id, (x, y))
            self.players_layer.add(self.players[id])
        self.players[id].rotation = rot
        self.players[id].x = x
        self.players[id].y = y
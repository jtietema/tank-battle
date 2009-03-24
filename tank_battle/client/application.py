from hulknet.client.application import GenericClientApp


from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
from cocos.sprite import Sprite
import cocos.tiles
from tank_battle.tank import Tank
import tiled2cocos


class TankBattleClient(GenericClientApp):
    def __init__(self, clientFactoryClass):
        super(self.__class__, self).__init__(clientFactoryClass)
        self.players = {}
    
    def run(self):
        self.connect('10.9.8.80', 7777)
        
        director.init(caption='Tank Battle', width=800, height=600)

        self.current_map = tiled2cocos.load_map('map2.tmx')

        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)

        self.scroller = cocos.tiles.ScrollingManager()

        tank_layer = cocos.tiles.ScrollableLayer()
        tank = Tank((self.current_map.px_width // 2, self.current_map.px_height // 2), self)
        tank_layer.add(tank)
        
        self.players_layer = cocos.tiles.ScrollableLayer()

        self.scroller.add(self.current_map)
        self.scroller.add(self.players_layer)
        self.scroller.add(tank_layer)
        
        scene = Scene(self.scroller)
        
        scene.schedule(self.update)
        
        director.run(scene)
    
    def serverTankState(self, id, rot, (x,y)):
        if id not in self.players:
            self.players[id] = Tank((x,y))
            self.players_layer.add(self.players[id])
        self.players[id].rotation = rot
        self.players[id].x = x
        self.players[id].y = y
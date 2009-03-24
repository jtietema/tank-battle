from hulknet.client.application import GenericClientApp


from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
from cocos.sprite import Sprite
import cocos.tiles
from tank_battle.tank import Tank
import tiled2cocos


class TankBattleClient(GenericClientApp):    
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

        self.scroller.add(self.current_map)
        self.scroller.add(tank_layer)
        
        scene = Scene(self.scroller)
        
        scene.schedule(self.update)
        
        director.run(scene)
        
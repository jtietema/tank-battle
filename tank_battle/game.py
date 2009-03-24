from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
import cocos.actions
from cocos.sprite import Sprite
import tiled2cocos


director.init(caption='Tank Battle', width=800, height=600)

current_map = tiled2cocos.load_map('map2.tmx')

keyboard = key.KeyStateHandler()
director.window.push_handlers(keyboard)

scroller = cocos.tiles.ScrollingManager()

from tank import Tank

tank_layer = cocos.tiles.ScrollableLayer()
tank = Tank((current_map.px_width // 2, current_map.px_height // 2))
tank_layer.add(tank)

scroller.add(current_map)
scroller.add(tank_layer)


def run():
    director.run(Scene(scroller))

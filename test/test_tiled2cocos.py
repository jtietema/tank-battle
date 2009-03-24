import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
import cocos.actions
from cocos.sprite import Sprite
import math
import tiled2cocos

class Tank(Sprite):
    speed = 0
    accel = 20
    deccel = 15
    new = True
    
    def update(self, dt):
        self.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        
        # TODO: time-based accel/deccel
        
        if keyboard[key.UP] or keyboard[key.DOWN]:
            self.speed += (keyboard[key.UP] - keyboard[key.DOWN]) * self.accel
            self.speed = min(200, max(-100, self.speed))
        else:
            if self.speed < 0:
                self.speed += self.deccel
                self.speed = min(self.speed, 0)
            elif self.speed > 0:
                self.speed -= self.deccel
                self.speed = max(self.speed, 0)
            elif not self.new:
                return
        
        if self.new:
            self.new = False
        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        new_x = self.x + math.sin(r) * s
        new_y = self.y + math.cos(r) * s
        
        tile_properties = test_map.get_at_pixel(new_x, new_y).tile.properties
        if not 'collision' in tile_properties:
            self.x = new_x
            self.y = new_y
            scroller.set_focus(self.x, self.y)

if __name__ == '__main__':
    director.init(caption='Tank Battle', width=800, height=600)
    
    test_map = tiled2cocos.load_map('map2.tmx')
    
    tank_layer = cocos.tiles.ScrollableLayer()
    tank = Tank('tank.png')
    tank.x = test_map.px_width // 2
    tank.y = test_map.px_height // 2
    tank.schedule(tank.update)
    tank_layer.add(tank)
    
    scroller = cocos.tiles.ScrollingManager()
    scroller.add(test_map)
    scroller.add(tank_layer)
    
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    
    director.run(Scene(scroller))

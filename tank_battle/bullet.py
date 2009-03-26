from cocos.sprite import Sprite
import math


# The speed of the bullet. The bullet has no acceleration - it is always at full
# speed.
SPEED = 400


class Bullet(Sprite):
    def __init__(self, id, rotation, pos, app):
        self.app = app
        self.id = id
        
        self.pos = pos
        Sprite.__init__(self, 'bullet.png', pos)
        
        self.rotation = rotation
        
        self.schedule(self.update)
    
    def update(self, dt):
        r = math.radians(self.rotation)
        s = dt * SPEED
        
        self.x += math.sin(r) * s
        self.y += math.cos(r) * s
        
        left = self.x - self.image_anchor_x
        right = self.x + self.image_anchor_x
        
        top = self.y + self.image_anchor_y
        bottom = self.y - self.image_anchor_y
        
        if top < 0 or right < 0 or left > self.app.current_map.px_width or bottom > self.app.current_map.px_height:
            self.app.remove_bullet(self.id)
        
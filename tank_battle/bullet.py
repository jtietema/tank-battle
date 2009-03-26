from cocos.sprite import Sprite
import math


# The speed of the bullet. The bullet has no acceleration - it is always at full
# speed.
SPEED = 400


class Bullet(Sprite):
    def __init__(self, id, rotation, pos):
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
        
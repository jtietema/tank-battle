from cocos.sprite import Sprite
from pyglet.window import key
import math

from game import keyboard, scroller, current_map


FORWARD     = 1
STILL       = 0
REVERSE     = -1

MAX_SPEEDS = {
    FORWARD:    200,
    STILL:      0,
    REVERSE:    100
}

# Time it takes to get from zero to 100, in seconds. We use linear
# acceleration.
ACCEL_TIME = 1

# Time it takes to brake from 100 to zero, in seconds.
BRAKE_TIME = 0.5

# Time it takes from slow down naturally from 100 to zero, in
# seconds.
SLOW_DOWN_TIME = 2

# The speed at which the tank can rotate. The tank can rotate while
# not driving.
ROTATION_SPEED = 150


def signum(number):
    if number > 0: return 1
    elif number < 0: return -1
    return number


class Tank(Sprite):
    """A tank in the game."""
    
    def __init__(self, (x, y)):
        """Initializes a new tank sprite."""
        super(self.__class__, self).__init__('tank.png')
        
        # The tank's current speed.
        self.speed = 0
        
        # Set the tank's initial position.
        self.x, self.y = x, y
        
        # Make sure the update method is called on every frame.
        self.schedule(self.update)
    
    def update(self, dt):
        """Updates the tank's state based on the amount of time passed since the last
        update call."""
        
        # Determine the tank's rotation signum. Since the operands are booleans, which
        # effectively map to the integers 0 and 1, we can use them for arithmetic.
        rotation_signum = keyboard[key.RIGHT] - keyboard[key.LEFT]
        
        self.rotation += rotation_signum * ROTATION_SPEED * dt
        self.speed = self.calculate_speed(dt)
        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        target_x = self.x + math.sin(r) * s
        target_y = self.y + math.cos(r) * s
        
        if self.is_valid_move((target_x, target_y)):
            # The target location is a valid move, so execute it.
            self.x = target_x
            self.y = target_y
            scroller.set_focus(self.x, self.y)
    
    def calculate_speed(self, dt):
        """Calculates the tank's speed based on the time passed since the last update
        call."""
        driving_signum = keyboard[key.UP] - keyboard[key.DOWN]
        
        speed = self.speed
        
        if speed is 0:
            max_speed = MAX_SPEEDS[driving_signum]
        else:
            max_speed = MAX_SPEEDS[signum(speed)]
            
        time_factor = max_speed / 100

        if speed > 0:
            # Driving forward
            if driving_signum > 0:
                # Still accelerating
                speed += dt / ACCEL_TIME * time_factor * max_speed
                speed = min(speed, max_speed)
            elif driving_signum < 0:
                # Braking
                speed -= dt / BRAKE_TIME * time_factor * max_speed
            else:
                # Slowing down just by friction
                speed -= dt / SLOW_DOWN_TIME * time_factor * max_speed
                speed = max(speed, 0)

        elif speed < 0:
            # Driving in reverse
            if driving_signum < 0:
                # Still accelerating
                speed -= dt / ACCEL_TIME * time_factor * max_speed
                speed = max(speed, -max_speed)
            elif driving_signum > 0:
                # Braking
                speed += dt / BRAKE_TIME * time_factor * max_speed
            else:
                # Slowing down just by friction
                speed += dt / SLOW_DOWN_TIME * time_factor * max_speed
                speed = min(speed, 0)

        else:
            # Standing still
            if driving_signum > 0:
                # Accelerating forward
                speed += dt / ACCEL_TIME * time_factor * max_speed
                speed = min(speed, max_speed)
            elif driving_signum < 0:
                # Accelerating backward
                speed -= dt / BACKWARD_ACCEL_TIME * time_factor * max_speed
                speed = max(speed, -max_speed)
        
        print 'SIGNUM', driving_signum
        print 'SPEED', speed
        
        return speed
    
    def is_valid_move(self, (target_x, target_y)):
        """Determines if the move designated by the target position tuple passed
        in is a valid move, i.e. it does not cause any collisions."""
        tile_properties = current_map.get_at_pixel(target_x, target_y).tile.properties
        return not 'collision' in tile_properties

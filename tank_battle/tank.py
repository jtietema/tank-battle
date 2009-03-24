from cocos.sprite import Sprite
from pyglet.window import key
import math


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
ACCEL_TIME = 0.7

# Time it takes to brake from 100 to zero, in seconds.
BRAKE_TIME = 0.4

# Time it takes from slow down naturally from 100 to zero, in
# seconds.
SLOW_DOWN_TIME = 2

# The speed at which the tank can rotate. The tank can rotate while
# not driving.
ROTATION_SPEED = 150


def signum(number):
    """This should be in Python's standard library, but it isn't."""
    if number > 0: return 1
    elif number < 0: return -1
    return number
    

class Tank(Sprite):
    """A tank in the game."""
    
    def __init__(self, (x, y)):
        """Initializes a new tank sprite."""
        
        super(self.__class__, self).__init__('tank.png')
        
        # Set the tank's initial position.
        self.x, self.y = x, y


class PlayerTank(Tank):
    """Specialized version of a tank that can be controlled by the player."""
        
    def __init__(self, pos, app):
        """Initializes a new player tank sprite."""
        
        super(self.__class__, self).__init__(pos)
        
        # Keep a reference to the main application so we can access its
        # attributes when needed.
        self.app = app
        
        # The tank's current speed.
        self.speed = 0
        
        # Remember the tank's previous state so we can determine if we need
        # to send an update across the network.
        self.previous_state = None
        
        # Make sure the update method is called on every frame.
        self.schedule(self.update)
        
        self.schedule_interval(self.send_state, 0.02)
    
    def update(self, dt):
        """Updates the tank's state based on the amount of time passed since the last
        update call."""
        
        # Determine the tank's rotation signum. Since the operands are booleans, which
        # effectively map to the integers 0 and 1, we can use them for arithmetic.
        rotation_signum = self.app.keyboard[key.RIGHT] - self.app.keyboard[key.LEFT]
        
        self.rotation += (rotation_signum * ROTATION_SPEED * dt)
        
        # Make sure the rotation does not get larger than 360 degrees to decrease
        # network traffic.
        self.rotation = self.rotation % 360
        
        self.speed = self.calculate_speed(dt)
        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        target_x = self.x + math.sin(r) * s
        target_y = self.y + math.cos(r) * s
        
        if self.is_valid_move((target_x, target_y)):
            # The target location is a valid move, so execute it.
            self.x = target_x
            self.y = target_y
            
            # Make sure the tank stays in the center of the screen.
            self.app.scroller.set_focus(self.x, self.y)
    
    def send_state(self, dt):
        """Sends the tank's current state to the server."""
        if self.app.player is not None and self.previous_state <> (self.rotation, self.x, self.y):
            self.app.player.protocol.sendTankState(1, self.rotation, (self.x, self.y))
            
            # Store the tank's current state so we can compare it later to see if
            # we should send the tank's update state to the server.
            self.previous_state = (self.rotation, self.x, self.y)
    
    def calculate_speed(self, dt):
        """Calculates the tank's speed based on the time passed since the last update
        call."""
        driving_signum = self.app.keyboard[key.UP] - self.app.keyboard[key.DOWN]
        
        # Make a copy of the current speed, since we don't want to change it
        # directly (this is not an in-place method).
        speed = self.speed
        
        if speed is 0:
            # From stationary, the max speed is determined by the direction
            # we are driving (forward or reverse).
            max_speed = MAX_SPEEDS[driving_signum]
        else:
            # When driving, the current driving direction determines the
            # maximum speed.
            max_speed = MAX_SPEEDS[signum(speed)]
        
        # Since the maximum speed is defined in seconds it takes to get from
        # 0 to 100, we correct the actual time value by multiplying it with
        # a factor.
        time_factor = max_speed / 100

        if speed > 0:
            # Driving forward
            if driving_signum > 0:
                # Still accelerating
                speed += (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = min(speed, max_speed)
            elif driving_signum < 0:
                # Braking
                speed -= (dt / (BRAKE_TIME * time_factor)) * max_speed
            else:
                # Slowing down just by friction
                speed -= (dt / (SLOW_DOWN_TIME * time_factor)) * max_speed
                speed = max(speed, 0)

        elif speed < 0:
            # Driving in reverse
            if driving_signum < 0:
                # Still accelerating
                speed -= (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = max(speed, -max_speed)
            elif driving_signum > 0:
                # Braking
                speed += (dt / (BRAKE_TIME * time_factor)) * max_speed
            else:
                # Slowing down just by friction
                speed += (dt / (SLOW_DOWN_TIME * time_factor)) * max_speed
                speed = min(speed, 0)

        else:
            # Standing still
            if driving_signum > 0:
                # Accelerating forward
                speed += (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = min(speed, max_speed)
            elif driving_signum < 0:
                # Accelerating backward
                speed -= (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = max(speed, -max_speed)
        
        return speed
    
    def is_valid_move(self, (target_x, target_y)):
        """Determines if the move designated by the target position tuple passed
        in is a valid move, i.e. it does not cause any collisions."""
        tile_properties = self.app.current_map.get_at_pixel(target_x, target_y).tile.properties
        return not 'collision' in tile_properties

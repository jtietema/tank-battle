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
SLOW_DOWN_TIME = 1.5

# The speed at which the tank can rotate. The tank can rotate while
# not driving.
ROTATION_SPEED = 150


def signum(number):
    """This should be in Python's standard library."""
    if number > 0: return 1
    elif number < 0: return -1
    return number
    

class Tank(Sprite):
    """A tank in the game."""
    
    def __init__(self, id, pos, app):
        """Initializes a new tank sprite."""
        
        Sprite.__init__(self, 'tank.png', pos)
        
        # Unique ID to reference this tank through the network. Generated
        # by the server.
        self.id = id
        
        # Keep a reference to the main application so we can access its
        # attributes when needed.
        self.app = app
        
        # The tank's current speed.
        self.speed = 0
        
        self.schedule(self.update)
        
        self.rotation_signum = 0
        self.driving_signum = 0
        
        self.updated_by_network = False
    
    def move(self, dt):
        """Moves the tank based on the sprite's rotation, speed and x and y attributes.
        Returns True if the move could be performed, False otherwise."""        
        r = math.radians(self.rotation)
        s = dt * self.speed
        
        target_x = self.x + math.sin(r) * s
        target_y = self.y + math.cos(r) * s
        
        if self.is_valid_move((target_x, target_y)):
            # The target location is a valid move, so execute it.
            self.x = target_x
            self.y = target_y
            return True
        
        return False
    
    def update(self, dt):        
        """Since additional data comes in asynchronously, we interpolate by simply
        doing another move using the current state of the tank."""
        if self.updated_by_network:
            self.updated_by_network = False
            return
        
        self.rotation += (self.rotation_signum * ROTATION_SPEED * dt)
        self.rotation = self.rotation % 360
        
        self.speed = self.calculate_speed(dt)                                                                                                                                                                                                            
        
        self.move(dt)
    
    def sync_state(self, rot, rot_signum, speed, driving_signum, (x, y)):
        """Called when the network receives an updated state for this tank."""
        self.rotation = rot
        self.rotation_signum = rot_signum
        self.speed = speed
        self.driving_signum = driving_signum
        self.x = x
        self.y = y
        
        self.updated_by_network = True
    
    def is_valid_move(self, (target_x, target_y)):
        """Determines if the move designated by the target position tuple passed
        in is a valid move, i.e. it does not cause any collisions."""
        cells = self.app.current_map.get_in_region(target_x, target_y, target_x + self.width, target_y + self.height)

        for cell in cells:
            if 'blocked' in cell.tile.properties:
                return False

        return True
    
    def calculate_speed(self, dt):
        """Calculates the tank's speed based on the time passed since the last update
        call."""
        speed = self.speed

        if speed is 0:
            max_speed = MAX_SPEEDS[self.driving_signum]
        else:
            max_speed = MAX_SPEEDS[signum(speed)]

        time_factor = max_speed / 100

        if speed > 0:
            # Driving forward
            if self.driving_signum > 0:
                # Still accelerating
                speed += (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = min(speed, max_speed)
            elif self.driving_signum < 0:
                # Braking
                speed -= (dt / (BRAKE_TIME * time_factor)) * max_speed
            else:
                # Slowing down just by friction
                speed -= (dt / (SLOW_DOWN_TIME * time_factor)) * max_speed
                speed = max(speed, 0)

        elif speed < 0:
            # Driving in reverse
            if self.driving_signum < 0:
                # Still accelerating
                speed -= (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = max(speed, -max_speed)
            elif self.driving_signum > 0:
                # Braking
                speed += (dt / (BRAKE_TIME * time_factor)) * max_speed
            else:
                # Slowing down just by friction
                speed += (dt / (SLOW_DOWN_TIME * time_factor)) * max_speed
                speed = min(speed, 0)

        else:
            # Standing still
            if self.driving_signum > 0:
                # Accelerating forward
                speed += (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = min(speed, max_speed)
            elif self.driving_signum < 0:
                # Accelerating backward
                speed -= (dt / (ACCEL_TIME * time_factor)) * max_speed
                speed = max(speed, -max_speed)

        return speed


class PlayerTank(Tank):
    """Specialized version of a tank that can be controlled by the player."""
        
    def __init__(self, id, pos, app):
        """Initializes a new player tank sprite."""
        
        Tank.__init__(self, id, pos, app)
        
        # Remember the tank's previous state so we can determine if we need
        # to send an update across the network.
        self.previous_state = None
        
        self.schedule_interval(self.send_state, 0.05)
    
    def update(self, dt):
        """Updates the tank's state based on the amount of time passed since the last
        update call."""
        
        # Determine the tank's rotation signum. Since the operands are booleans, which
        # effectively map to the integers 0 and 1, we can use them for arithmetic. We
        # store the rotation signum on the object because we want to send it over the
        # network to improve interpolation.
        self.rotation_signum = self.app.keyboard[key.RIGHT] - self.app.keyboard[key.LEFT]
        self.driving_signum = self.app.keyboard[key.UP] - self.app.keyboard[key.DOWN]
        
        self.rotation += (self.rotation_signum * ROTATION_SPEED * dt)
        
        # Make sure the rotation does not get larger than 360 degrees to decrease
        # network traffic.
        self.rotation = self.rotation % 360
        
        self.speed = self.calculate_speed(dt)
        
        if self.move(dt):
            self.app.scroller.set_focus(self.x, self.y)
    
    def send_state(self, dt):
        """Sends the tank's current state to the server."""
        current_state = (self.rotation, self.rotation_signum, self.speed, self.driving_signum, (self.x, self.y))
        if self.app.player is not None and self.previous_state <> current_state:
            self.app.player.protocol.sendTankState(self.id, *current_state)
            
            self.previous_state = current_state

from cocos.sprite import Sprite
from pyglet.window import key
import math

from pathfinder import Pathfinder

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
    
    def __init__(self, id, pos):
        """Initializes a new tank sprite."""
        
        Sprite.__init__(self, 'tank.png', pos)
        
        self.id = id


class PlayerTank(Tank):
    """Specialized version of a tank that can be controlled by the player."""
        
    def __init__(self, id, pos, app):
        """Initializes a new player tank sprite."""
        
        Tank.__init__(self, id, pos)
        
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
            self.app.scroller.set_focus(self.x, self.y)
    
    def send_state(self, dt):
        """Sends the tank's current state to the server."""
        if self.app.player is not None and self.previous_state <> (self.rotation, self.x, self.y):
            self.app.player.protocol.sendTankState(self.id, self.rotation, (self.x, self.y))
            self.previous_state = (self.rotation, self.x, self.y)
    
    def calculate_speed(self, dt):
        """Calculates the tank's speed based on the time passed since the last update
        call."""
        driving_signum = self.app.keyboard[key.UP] - self.app.keyboard[key.DOWN]
        
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
        cells = self.app.current_map.get_in_region(target_x, target_y, target_x + self.width, target_y + self.height)
        
        for cell in cells:
            if 'collision' in cell.tile.properties:
                return False
        
        return True

class ComputerTank(Tank):
    def __init__(self, id, pos, app):
        Tank.__init__(self, id, pos)
        
        self.path = None
        self.dest = None
        self.rot_dest = None
        self.app = app
        self.pathfinder = Pathfinder(self.is_valid_move)
    
    def update(self, dt):
        '''If there is a path follow it, otherwise calculate one'''
        if self.path is not None:
            self.do_move(dt)
        elif self.pathfinder is not None:
            self.find_path()
    
    def do_move(self, dt):
        '''Does all the moving logic of the AI tank'''
        if self.dest is None:
            self.next_dest()
        if self.dest is self.xy:
            self.next_dest()
        else:
            if self.rot_dest is self.rotation:
                # do the moving
                self.speed = 50
                #self.move(dt)
            elif self.rot_dest is None:
                # calculate new rot_dest
                self.calc_rotate()
            else:
                # rotate some more
                self.do_rotate()
    
    def calc_rotate(self):
        '''Calculate the new rotation to the destination'''
        x, y = self.xy
        dest_x, dest_y = self.dest
        # calculate the angle
        dx = abs(x - dest_x)
        dy = abs(y - dest_y)
        h = math.sqrt(dx**2 + dy**2)
        delta_rot = math.asin(dx / h)
        
        # we now have the delta, but we need to compensate for the quadrant it is in
        # eg. right top(0), right bottom(90), left bottom(180) and left top(270)
        
        # find the quadrant
        right = top = True
        if x > dest_x:
            right = False
        if y > dest_y:
            top = False
        
        # correct the angle to rotation
        if right and not top:
            delta_rot += 90
        if not right and not top:
            delta_rot += 180
        if top and not right:
            delta_rot += 270
        
        # save the calculated new rotation in the class
        self.dest_rot = delta_rot
    
    def do_rotate(self):
        '''Rotates the Tank (max 5 degrees per update)'''
        rot = min(abs(self.rotation - self.rot_dest), 5)
        if self.rotation > self.rot_dest:
            self.rotation -= rot # rotate left
        else:
            self.rotatation += rot # rotate right
    
    def next_dest(self):
        '''Pick the next destination from the path queue (if present)'''
        if len(self.path) > 0:
            dest_ij = self.path.pop(0)
            cell = self.app.current_map.get_cell(*dest_ij)
            self.dest = cell.center
            self.rot_dest = None
        else:
            self.path = None
    
    def find_path(self):
        '''Do pathfinding stuff'''
        result = Pathfinder.NOT_DONE
        while result is Pathfinder.NOT_DONE:
            result = self.pathfinder.iteratePath()
        if result.FOUND_GOAL:
            self.path = self.pathfinder.finishPath()
            self.pathfinder = None
        if result.IMPOSSIBLE:
            self.pathfinder = None
    
    def is_valid_move(self, i,j):
        '''Checks if the tile is blocked (used by pathfinding code)'''
        cell = self.app.current_map.get_cell(i,j)
        if 'blocked' in cell.tile.properties:
            return False
        return True

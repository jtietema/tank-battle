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
    
    image_file = 'tank.png'
    
    def __init__(self, id, pos, app):
        """Initializes a new tank sprite."""
        
        Sprite.__init__(self, self.image_file, pos)
        
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
        else:
            # Reset the tank's speed, we've come to a sudden halt.
            self.speed = 0
            
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
        cells = self.app.current_map.get_in_region(target_x, target_y, target_x + self.width / 2, target_y + self.height / 2)

        for cell in cells:
            if 'blocked' in cell.tile.properties:
                return False

        return True
    
    def calculate_speed(self, dt):
        """Calculates the tank's speed based on the time passed since the last update
        call."""
        speed = self.speed

        if speed == 0:
            max_speed = MAX_SPEEDS[self.driving_signum]
        else:
            max_speed = MAX_SPEEDS[signum(speed)]
        if max_speed == 0:
            return 0

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

    def send_state(self, dt):
        """Sends the tank's current state to the server."""
        current_state = (self.rotation, self.rotation_signum, self.speed, self.driving_signum, (self.x, self.y))
        if self.app.player is not None and self.previous_state <> current_state:
            self.app.player.protocol.sendTankState(self.id, *current_state)
            
            self.previous_state = current_state

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
    
    def fire(self):
        """Fires a bullet."""
        self.app.player.protocol.sendFire(self.id, self.rotation, (self.x, self.y))
    
class ComputerTank(Tank):
    image_file = 'ai-tank.png'
    
    def __init__(self, id, pos, app):
        Tank.__init__(self, id, pos, app)
        self.path = None
        self.dest = (10,10)
        self.idest = None
        self.rot_dest = None
        self.rotation_signum = 0
        self.driving_signum = 0
        self.previous_state = None
        self.pathfinder = Pathfinder(self.is_valid_cell)
        dx, dy = self.dest
        dcell = self.app.current_map.get_at_pixel(dx, dy)
        x,y = self.position
        cell = self.app.current_map.get_at_pixel(x, y)
        self.pathfinder.setupPath(cell.i, cell.j, dcell.i, dcell.j)
    
    def update(self, dt):
        '''If there is a path follow it, otherwise calculate one'''
        if self.path is not None:
            self.do_move(dt)
        elif self.pathfinder is not None:
            self.find_path()
    
    def do_move(self, dt):
        '''Does all the moving logic of the AI tank'''
        if self.idest is None:
            self.next_dest()
        if abs(self.idest[0] - self.position[0]) < 10 and abs(self.idest[1] - self.position[1]) < 10:
            self.next_dest()
        else:
            # calculate new rot_dest
            self.calc_rotate()
            if self.rot_dest == self.rotation:
                # do the moving
                self.speed = 50
                self.move(dt)
            else:
                # rotate some more
                self.do_rotate()
            self.send_state(dt)
    
    def calc_rotate(self):
        '''Calculate the new rotation to the destination'''
        x, y = self.position
        dest_x, dest_y = self.idest
        # calculate the angle
        dx = abs(x - dest_x)
        dy = abs(y - dest_y)
        h = math.sqrt(dx**2 + dy**2)
        delta_rot = math.degrees(math.asin(dx / h))

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
        self.rot_dest = delta_rot

    def do_rotate(self):
        '''Rotates the Tank (max 5 degrees per update)'''
        rot = min(abs(self.rotation - self.rot_dest), 5)
        if self.rotation > self.rot_dest:
            self.rotation -= rot # rotate left
        else:
            self.rotation += rot # rotate right
    
    def next_dest(self):
        '''Pick the next destination from the path queue (if present)'''
        if len(self.path) > 0:
            dest_xy = self.path.pop(0)
            self.idest = dest_xy
            self.rot_dest = None
        else:
            self.path = None
    
    def find_path(self):
        '''Do pathfinding stuff'''
        result = Pathfinder.NOT_DONE
        while result is Pathfinder.NOT_DONE:
            result = self.pathfinder.iteratePath()
        if result is Pathfinder.FOUND_GOAL:
            self.path = self.pathfinder.finishPath()
            self.path = map(self.ij_to_xy, self.path)
            self.pathfinder = None
        if result is Pathfinder.IMPOSSIBLE:
            self.pathfinder = None
    
    def is_valid_cell(self, i,j):
        '''Checks if the tile is blocked (used by pathfinding code)'''
        cell = self.app.current_map.get_cell(i,j)
        if cell is None or 'blocked' in cell.tile.properties:
            return False
        return True

    def ij_to_xy(self, ij):
        return self.app.current_map.get_cell(*ij).center

    def xy_to_ij(self, xy):
        cell = self.app.current_map.get_at_pixel(*xy)
        return (cell.i, cell.j)

    def is_valid_move(self, (x,y)):
        return True


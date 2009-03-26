from hulknet.client.application import GenericClientApp

import sys
from cocos.director import director
from cocos.scene import Scene
from pyglet.window import key
from cocos.sprite import Sprite
import cocos.tiles
from tank_battle.tank import Tank, PlayerTank, ComputerTank
from tank_battle.bullet import Bullet
import tiled2cocos


class TankBattleClient(GenericClientApp):
    def __init__(self, clientFactoryClass):
        GenericClientApp.__init__(self,clientFactoryClass)
        self.players = {}
        self.bullets = {}
        self.tank_layer = None
        self.tank = None
        self.computer_players = []
    
    def run(self):
        director.init(caption='Tank Battle', width=800, height=600)

        self.current_map = tiled2cocos.load_map('maps/map2.tmx')

        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        director.window.push_handlers(self.on_key_press)

        self.scroller = cocos.tiles.ScrollingManager()
        
        self.sprites_layer = cocos.tiles.ScrollableLayer()

        self.scroller.add(self.current_map)
        self.scroller.add(self.sprites_layer)
        
        scene = Scene(self.scroller)
        
        scene.schedule(self.update)
        
        self.connect(sys.argv[1], 7777)
        
        director.show_FPS = True
        
        director.run(scene)
    
    def update(self, dt):
        GenericClientApp.update(self, dt)
        for tank in self.computer_players:
            tank.update(dt)
        
    def remove_bullet(self, bullet_id):
        print 'remove_bullet', bullet_id
        self.sprites_layer.remove(self.bullets[id])
        del self.bullets[id]
    
    def on_key_press(self, k, modifier):
        if k == key.A:
            self.requestTankId()
        elif k == key.SPACE and self.tank is not None:
            self.tank.fire()
    
    def requestTankId(self):
        self.player.protocol.sendTankId()
    
    def serverTankID(self, id):
        if not self.tank_layer:
            self.tank_layer = cocos.tiles.ScrollableLayer()
            self.tank = PlayerTank(id, ((self.current_map.px_width // 2), (self.current_map.px_height // 2)), self)
            self.tank_layer.add(self.tank)
            self.players[id] = self.tank
            self.scroller.add(self.tank_layer)
        else:
            ai_tank = ComputerTank(id, self.tank.position, self)
            self.computer_players.append(ai_tank)
            self.players[id] = ai_tank
            self.tank_layer.add(ai_tank)
    
    def serverTankRemove(self, id):
        self.sprites_layer.remove(self.players[id])
        del self.players[id]
    
    def serverTankState(self, id, rot, rot_signum, speed, driving_signum, pos):
        if id not in self.players:
            self.players[id] = Tank(id, pos, self)
            self.sprites_layer.add(self.players[id])
            
        self.players[id].sync_state(rot, rot_signum, speed, driving_signum, pos)
    
    def serverFire(self, bullet_id, rotation, pos):
        bullet = Bullet(bullet_id, rotation, pos, self)
        self.bullets[id] = bullet
        self.sprites_layer.add(bullet)

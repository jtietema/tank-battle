import sys
import os

from cocos.director import director
from cocos.scene import Scene
from cocos import tiles


if __name__ == '__main__':
    director.init(caption='Tank Battle', width=448, height=336)
    
    maps = tiles.load('maps.xml')
    
    print maps['map0']
    
    scroller = tiles.ScrollingManager()
    scroller.add(maps['map0'])

    director.run(Scene(scroller))
    
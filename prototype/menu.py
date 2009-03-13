import sys
import os

from cocos.director import director
from cocos.scene import Scene
from cocos import menu, layer


class MenuScene(Scene):
    def __init__(self):
        """Creates a new menu scene."""
        mplayer = layer.MultiplexLayer(
            MainMenu(),
            OptionsMenu()
        )
        
        super(self.__class__, self).__init__(mplayer)


class MainMenu(menu.Menu):
    def __init__(self):
        """Creates the main menu for the game."""
        super(self.__class__, self).__init__('Tank Battle')
        
        items = [
            menu.MenuItem('New Game', self.on_new_game),
            menu.MenuItem('Options', self.on_options),
            menu.MenuItem('Quit', self.on_quit)
        ]
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_new_game(self):
        """Called when the user selects 'New Game'."""
        pass
    
    def on_options(self):
        """Called when the user selects 'Options'."""
        self.parent.switch_to(1)
    
    def on_quit(self):
        """Called when the user selects 'Quit'."""
        sys.exit()


class OptionsMenu(menu.Menu):
    # TODO: make dynamic
    AVAILABLE_RESOLUTIONS = ('640x480', '800x600', '1024x768')
    
    def __init__(self):
        """Initializes the options menu."""
        super(self.__class__, self).__init__('Options')
        
        items = [
            self.create_resolution_item(),
            self.create_volume_item()
        ]
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def create_resolution_item(self):
        """Helper method to create the resolution menu item for this
        menu."""        
        return menu.MultipleMenuItem(
            'Resolution:',
            self.on_resolution_changed,
            self.__class__.AVAILABLE_RESOLUTIONS,
            0
        )
    
    def on_resolution_changed(self, index):
        """Called when the user changes the resolution."""
        ar = self.__class__.AVAILABLE_RESOLUTIONS
        
        # Width and height should be of type int to work properly.
        width, height = map(int, ar[index].split('x'))
        
        director.window.set_size(width, height)
    
    def create_volume_item(self):
        """Helper method to create the volume item for the menu."""
        return menu.MultipleMenuItem(
            'Volume:',
            self.on_volume_changed,
            map(str, range(0, 11)),
            7
        )
    
    def on_volume_changed(self, index):
        """Called when the volume is changed."""
        print 'VOLUME:', index

    def on_quit(self):
        """Called when the escape button is pressed. Switches back to
        the main menu."""
        self.parent.switch_to(0)


if __name__ == '__main__':
    director.init(caption='Tank Battle')

    director.run(MenuScene())
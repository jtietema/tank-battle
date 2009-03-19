import sys
import os

from cocos.director import director
from cocos.scene import Scene
from cocos import menu, layer


class MenuScene(Scene):    
    def __init__(self):
        """Creates a new menu scene."""        
        super(self.__class__, self).__init__()
        
        self.add(layer.MultiplexLayer(
            MainMenu(),
            NewGameMenu(),
            OptionsMenu()
        ))


class MainMenu(menu.Menu):    
    def __init__(self):
        """Creates the main menu for the game."""
        super(self.__class__, self).__init__('Tank Battle')
        
        items = [
            menu.MenuItem('New Game', self.on_new_game),
            menu.MenuItem('Options', self.on_options),
            menu.MenuItem('Quit', self.on_quit_button)
        ]
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_new_game(self):
        """Called when the user selects 'New Game'."""
        self.parent.switch_to(1)
    
    def on_options(self):
        """Called when the user selects 'Options'."""
        self.parent.switch_to(2)
    
    def on_quit_button(self):
        """Called when the user selects 'Quit'. Quits the game."""
        sys.exit()
        
    def on_quit(self):
        """Called when the user presses ESC. This prevents the game from
        quitting when pressing ESC in the main menu."""
        pass


class NewGameMenu(menu.Menu):
    # TODO: implement
    def __init__(self):
        """Initializes the new game menu."""
        super(self.__class__, self).__init__('New Game')
        
        items = [
            menu.EntryMenuItem('Server:', self.on_server_text, ''),
            menu.MenuItem('Start', self.on_start)
        ]
        
        self.create_menu(items, menu.shake(), menu.shake_back())
    
    def on_server_text(self, text):
        """Called when the text is typed in the 'Server' field."""
        print text
    
    def on_start(self):
        """Called when start is selected."""
        # TODO: do something useful
        print 'START'
    
    def on_quit(self):
        """Called when the user presses ESC. Moves back to the main
        menu."""
        self.parent.switch_to(0)


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
            0 # TODO: make dynamic
        )
    
    def on_resolution_changed(self, index):
        """Called when the user changes the resolution."""
        ar = self.__class__.AVAILABLE_RESOLUTIONS
        
        # Width and height should be of type int to work properly.
        width, height = map(int, ar[index].split('x'))
        
        director.window.set_size(width, height)
        
        # TODO: save
    
    def create_volume_item(self):
        """Helper method to create the volume item for the menu."""
        return menu.MultipleMenuItem(
            'Volume:',
            self.on_volume_changed,
            # Options should be str objects to work properly.
            map(str, range(0, 11)),
            7 # TODO: make dynamic
        )
    
    def on_volume_changed(self, index):
        """Called when the volume is changed."""
        print 'VOLUME:', index # TODO: save

    def on_quit(self):
        """Called when the escape button is pressed. Switches back to
        the main menu."""
        self.parent.switch_to(0)


if __name__ == '__main__':
    director.init(caption='Tank Battle')

    director.run(MenuScene())
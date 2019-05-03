import pride.gui.gui
import pride.components.user

import game3.gui.character


class Game_Window(pride.gui.gui.Application):

    defaults = {"character_screen_type" : game3.gui.character.Character_Selection_Screen}
    autoreferences = ("character_selection_screen", )

    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        self.background = self.application_window.create("game3.gui.stars.Star_Background",
                                                         pack_mode="main", star_count=256)

    def load_character_selection_screen(self, characters):
        self.character_selection_screen = self.background.create(self.character_screen_type,
                                                                 characters=characters)

import pride.gui.gui

import game3.gui.character


class Game_Window(pride.gui.gui.Application):

    defaults = {"character_screen_type" : game3.gui.character.Character_Selection_Screen}
    autoreferences = ("character_selection_screen", )

    def load_character_selection_screen(self, characters):
        self.character_selection_screen = self.application_window.create(self.character_screen_type,
                                                                         characters=characters)

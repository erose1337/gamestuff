from math import ceil, sqrt

import pride.gui.gui
from pride.functions.utilities import slide

import game3.character


class Character_Icon(pride.gui.gui.Button):

    def left_click(self, mouse):
        self.parent_application.view_character(self.character)


class New_Character_Icon(pride.gui.gui.Button):

    defaults = {"text" : "New Character",
                "tip_bar_text" : "Design and create a new character"}

    def left_click(self, mouse):
        self.parent_application.create_new_character()


#class Upload_Character_Icon(pride.gui.gui.Button):
#
#    defaults = {"text" : "Upload character"}


class Character_Selection_Screen(pride.gui.gui.Application):

    defaults = {"grid_type" : "pride.gui.grid.Grid", "characters" : tuple,
                "column_button_type" : "pride.gui.gui.Container",
                "info_viewer_type" : "game3.gui.actionmenu.Action_Menu",
                "startup_components" : tuple(), "tip_bar_enabled" : False,
                "character_editor_screen_type" : "game3.gui.charactersheet.Character_Screen"}
    autoreferences = ("viewer", "grid")

    def __init__(self, **kwargs):
        super(Character_Selection_Screen, self).__init__(**kwargs)
        self.create_characters()
    #    self.create_info_viewer()

    def create_characters(self):
        characters = self.characters
        size = max(2, int(ceil(sqrt(len(characters) + 1))))
        grid = self.application_window.create(self.grid_type, grid_size=(size, size),
                                              pack_mode="left")
        self.grid = grid
        for row_no, _characters in enumerate(slide(characters, size)):
            for column_no, character in enumerate(_characters):
                grid[row_no][column_no].create(Character_Icon, character=character)
        if characters and column_no - 1 == size:
            row_number += 1
            column_no = 0
        else:
            row_no = column_no = 0
        grid[row_no][column_no].create(New_Character_Icon)
        self.viewer = self.application_window.create("pride.gui.gui.Container", pack_mode="left")

    def view_character(self, character):
        if self.viewer is not None:
            self.viewer.hide()
        self.viewer = self.application_window.create(self.info_viewer_type, character=character,
                                                     pack_mode="left")

    def create_new_character(self):
        if self.viewer is not None:
            self.viewer.delete()
        if self.grid is not None:
            self.grid.hide()
        character = self.character = game3.character.Character()
        create = self.application_window.create
        self.character_editing_screen = create(self.character_editor_screen_type,
                                               character=character)

    def save_character(self):
        window = self.parent_application
        window.game_client.save_character(self.character.name, self.character.to_info())
        window.game_client.get_character_info()
        self.delete()

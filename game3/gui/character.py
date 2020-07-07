from math import ceil, sqrt

import pride.gui.gui
from pride.gui.widgets.form import field_info
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

    defaults = {"characters" : tuple,
                "column_button_type" : "pride.gui.gui.Container",
                "info_viewer_type" : "game3.gui.sheet.Character_Sheet",
                "startup_components" : tuple(), "tip_bar_enabled" : False,
                "character_editor_screen_type" : "game3.gui.sheet.Character_Sheet",
                "mode" : None}
    autoreferences = ("viewer", "character_editing_screen")

    def __init__(self, **kwargs):
        super(Character_Selection_Screen, self).__init__(**kwargs)
        self.create_character_listing()

    def create_character_listing(self):
        rows = slide(self.characters, 8)
        fields = [[field_info("view_character", button_text=_char.name,
                              args=(_char, )) for _char in row]
                   for row in rows]

        if self.mode == "creator":
            fields.append([field_info("create_new_character",
                                      button_text="New Character")])

        form = self.application_window.create("pride.gui.widgets.form.Form",
                                              fields=fields, max_rows=4,
                                            target_object=self, w_range=(0, .5),
                                         row_h_range=(0, .25), pack_mode="left")
        self.selector_window = form

    def view_character(self, character):
        mode = self.mode
        if mode == "arcade":
            read_only = True
        else:
            assert mode == "creator"
            read_only = False
        self.character = character
        self.viewer = self.application_window.create(self.info_viewer_type,
                                                     character=character,
                                                     pack_mode="left",
                                                     mode=mode,
                                                     read_only=read_only)
        if mode == "creator":
            self.selector_window.delete()

    def create_new_character(self):
        if self.character_editing_screen is not None:
            return # clicking on button twice could trigger this twice
        if self.viewer is not None:
            self.viewer.delete()
        character = self.character = game3.character.Character()
        create = self.application_window.create
        assert self.mode == "creator"
        self.character_editing_screen = create(self.character_editor_screen_type,
                                               character=character,
                                               mode="creator")

    def save_character(self):
        window = self.parent_application
        window.game_client.save_character(self.character.name,
                                          self.character.to_info())
        window.load_initial_window()
        self.delete()

    def exit_without_saving(self):
        self.parent_application.load_initial_window()
        self.delete()

    def select_character(self, character):
        self.parent_application.select_character(character)

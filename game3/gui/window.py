import os

import pride.gui.gui
import pride.gui.widgetlibrary

import character
import attributes
import affinities
import abilities


class Character_File_Selector(pride.gui.widgetlibrary.Field):

    defaults = {"field_name" : "filename", "initial_value" : '',
                "h_range" : (0, 80)}


class Game_Window(pride.gui.gui.Application):

    defaults = {"character_creation_screen_type" : "game3.gui.charactersheet.Character_Screen",
                "startup_components" : tuple()} # removes task bar from top
    mutable_defaults = {"_splash_screen_items" : list}

    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        self.splash_screen()

    def splash_screen(self):
        window = self.application_window
        image = window.create("pride.gui.images.Image", filename="./injuredcomic.bmp", pack_mode="top", color=(255, 125, 125, 255))
        bar = window.create("pride.gui.gui.Container", pack_mode="bottom", h_range=(0, 100), color=(255, 255, 255, 255))
        bar.create("pride.gui.widgetlibrary.Method_Button", text="Create character",
                   target=self.reference, method="create_character_screen",
                   pack_mode="left", scale_to_text=False)
        bar.create("pride.gui.widgetlibrary.Method_Button", text="Load character",
                   target=self.reference, method="load_character_screen",
                   pack_mode="left", scale_to_text=False)
        self._splash_screen_items = [image, bar]

    def create_character_screen(self):
        for item in self._splash_screen_items:
            item.delete()
        _character= character.Character(attributes=attributes.Attributes(),
                                        affinities=affinities.Affinities(),
                                        abilities=abilities.Abilities())
        self.character_screen = self.application_window.create(self.character_creation_screen_type,
                                                               character=_character).reference

    def load_character_screen(self):
        for item in self._splash_screen_items:
            item.delete()
        self.file_selector = self.application_window.create(Character_File_Selector,
                                                            write_field_method=self._load_character).reference

    def _load_character(self, field_name, value):
        if os.path.exists(value):
            pride.objects[self.file_selector].delete()
            status = self.create("pride.gui.gui.Container", text="Loading character...",
                                 h_range=(0, 80), pack_mode="bottom")
            pride.objects[self.sdl_window].run()
            _character = character.Character.from_sheet(value)
            status.delete()
            self.character_screen = self.application_window.create(self.character_creation_screen_type,
                                                                   character=_character).reference

    def _close_character_screen(self):
        pride.objects[self.character_screen].delete()
        self.splash_screen()

    def delete(self):
        super(Game_Window, self).delete()
        raise SystemExit()

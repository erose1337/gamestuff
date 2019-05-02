import os

import pride.gui.gui
import pride.gui.widgetlibrary

import character
import attributes
import affinities
import abilities
import gui.misc
import game3.gui.battle


class File_Selector(pride.gui.gui.Window):

    defaults = {"initial_value" : '', "file_category" : "misc",
                "delete_callback" : None, "tip_bar_enabled" : False,
                "recent_files" : dict()} # use 1 copy among all instances
    required_attributes = ("delete_callback", )
    autoreferences = ("selector", )

    def __init__(self, **kwargs):
        super(File_Selector, self).__init__(**kwargs)
        window = self#.application_window
        self.selector = window.create(pride.gui.widgetlibrary.Field,
                                      field_name="filename", initial_value=self.initial_value,
                                      h_range=(0, .10), write_field_method=self.write_field_method)
        bottom = window.create("pride.gui.gui.Container", pack_mode="bottom")
        recent_files = self.recent_files.setdefault(self.file_category, [])
        file_count = len(recent_files)
        for filename in recent_files:
            bottom.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                          method="write_field_method", args=("filename", filename, ),
                          h_range=(0, min(.10, 1.0 / file_count)),
                          text=filename, pack_mode="top", scale_to_text=False)

    def update_recent_files(self, value, file_category):
        recent_files = self.recent_files.setdefault(file_category, [value])
        if value in recent_files:
            recent_files.remove(value)
        if len(recent_files) == 10:
            recent_files[:] = [value] + recent_files[:-1]
        else:
            recent_files.insert(0, value)
        assert self.recent_files[file_category] is recent_files
        assert value in self.recent_files[file_category]

    def delete(self):
        super(File_Selector, self).delete()
        if self.delete_callback is not None:
            self.delete_callback()
        self.delete_callback = None


class Battle_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"text" : "Battle", "method" : "create_battle_screen",
                "pack_mode" : "left", "scale_to_text" : False,
                "tip_bar_text" : "Start a battle"}


class Create_Character_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"text" : "Create character", "method" : "create_character_screen",
                "pack_mode" : "left", "scale_to_text" : False,
                "tip_bar_text" : "Create a new character"}


class Load_Character_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"text" : "Load Character", "method" : "load_character_screen",
                "pack_mode" : "left", "scale_to_text" : False,
                "tip_bar_text" : "Load an existing character"}


class Options_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"text" : "options", "method" : "load_options_screen",
                "pack_mode" : "left", "scale_to_text" : False,
                "tip_bar_text" : "Modify game settings"}


class Game_Window(pride.gui.gui.Application):

    defaults = {"character_creation_screen_type" : "game3.gui.charactersheet.Character_Screen",
                "character_screen" : None, "options_screen" : None,
                "default_colors_filename" : "default.theme",
                "character" : None,
                "startup_components" : tuple()} # removes task bar from top
    mutable_defaults = {"_splash_screen_items" : list,
                        "recent_files" : lambda: {"character" : [],
                                                  "color" : [],
                                                  "misc" : []}}
    autoreferences = ("background", "battle_window", "character_screen",
                      "file_selector", "options_screen")

    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        gui.misc.set_theme_colors(self, self.default_colors_filename)
        self.splash_screen()

    def initialize_tip_bar(self):
        self.background = self.application_window.create("game3.gui.stars.Star_Background",
                                                         pack_mode="main", star_count=256)
        if self.tip_bar_enabled:
            self.tip_bar = self.background.create(self.tip_bar_type, h_range=(0, .05),
                                                  text="Tip bar", pack_mode="bottom",
                                                  center_text=False)

    def splash_screen(self):
        assert not self._splash_screen_items
        window = self.background
        #image = window.create("pride.gui.images.Image", filename="./injuredcomic.bmp", pack_mode="top", color=(255, 125, 125, 255))
        image = window.create("pride.gui.gui.Container", text="Title Screen", pack_mode="top")
        bar = window.create("pride.gui.gui.Container", pack_mode="bottom", h_range=(0, 100))#, color=(255, 255, 255, 255))
        bar.create(Battle_Button, target=self.reference)
        bar.create(Create_Character_Button, target=self.reference)
        bar.create(Load_Character_Button, target=self.reference)
        bar.create(Options_Button, target=self.reference)
        self._splash_screen_items = [image, bar]

    def clear_splash_screen(self):
        for item in self._splash_screen_items:
            item.delete()
        del self._splash_screen_items[:]

    def create_battle_screen(self):
        if self.character is None:
            self.show_status("Create/load character first", fade_duration=1.0)
        else:
            self.clear_splash_screen()
            character2 = character.Character(name="Test Character")
            event = game3.gui.battle.Battle_Event(characters=[self.character, character2])
            self.battle_window = self.background.create(game3.gui.battle.Battle_Window, event=event,
                                                        character=self.character,
                                                        participants=(self.character,
                                                                      character2))

    def create_character_screen(self):
        self.clear_splash_screen()
        _character= character.Character(attributes=attributes.Attributes(),
                                        affinities=affinities.Affinities(),
                                        abilities=abilities.Abilities())
        self.character = _character
        self.character_screen = self.background.create(self.character_creation_screen_type,
                                                       character=_character)

    def load_character_screen(self):
        self.clear_splash_screen()
        self.file_selector = self.background.create(File_Selector, file_category="character",
                                                    write_field_method=self._load_character,
                                                    delete_callback=self.splash_screen)

    def _load_character(self, field_name, value):
        if os.path.exists(value):
            selector = self.file_selector
            selector.update_recent_files(value, "character")
            selector.delete_callback = None
            selector.delete()
            self.file_selector = None
            background = self.background
            status = background.create("pride.gui.gui.Container", text="Loading character...",
                                       h_range=(0, 80), pack_mode="bottom")
            pride.objects[self.sdl_window].run()
            _character = character.Character.from_sheet(value)
            self.character = _character
            status.delete()
            self.character_screen = background.create(self.character_creation_screen_type,
                                                      character=_character)
            #self.update_recent_files(value, "character")

    def _close_character_screen(self):
        self.character_screen.delete()
        self.splash_screen()

    def load_options_screen(self):
        self.clear_splash_screen()
        self.options_screen = self.background.create("game3.gui.options.Options_Window")

    def _close_options_screen(self):
        self.options_screen.delete()
        self.splash_screen()

    def _close_to_title(self):
        if self.options_screen is not None:
            self.options_screen.delete()
        if self.character_screen is not None:
            self.character_screen.delete()
        self.splash_screen()

    def delete(self):
        self.teams = None
        self.character = None
        self.battle_window = None
        self.options_screen = None
        self.character_screen = None
        del self._splash_screen_items[:]
        super(Game_Window, self).delete()
        raise SystemExit()

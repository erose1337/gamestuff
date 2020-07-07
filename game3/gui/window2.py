import pride.gui.gui
import pride.gui.widgetlibrary
import pride.components.user
import pride.gui.widgets.form
field_info = pride.gui.widgets.form.field_info

import game3.gui.character

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
        self.selector.select(None) # auto-select file entry box so it doesn't have to be clicked on
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

    defaults = {"character_screen_type" : game3.gui.character.Character_Selection_Screen,
                "startup_components" : tuple(), "_splash_screen_items" : tuple(),
                "mode" : None}

    autoreferences = ("title_screen", "title_form",
                      "character_selection_screen", "game_client")

    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        self.application_window = self.application_window.create("game3.gui.stars.Star_Background",
                                                                 pack_mode="main", star_count=1024,
                                                                 animate=True)

    def load_initial_window(self):
        window = self.application_window
        self.title_screen = window.create("pride.gui.gui.Container",
                                          pack_mode="top", text="Superzero")

        fields = [[field_info("load_character_selector", button_text="Select Character",
                              entry_kwargs={"tip_bar_text" :
                                            "Select which character to play"}),
                   field_info("load_character_editor",
                              button_text="Character Editor",
                              entry_kwargs={"tip_bar_text" :
                                            "Design and customize characters"}),
                   field_info("handle_close", button_text="Exit",
                              entry_kwargs={"tip_bar_text" : "Exit the game"})
                 ]]
        form = window.create("pride.gui.widgets.form.Form", fields=fields,
                             pack_mode="bottom", h_range=(0, .1),
                             target_object=self)
        self.title_form = form

    def load_character_selector(self):
        self.title_screen.hide()
        self.title_form.hide()
        self.show_status("Acquiring character list...")
        self.game_client.get_character_info()
        self.mode = "arcade"

    def load_character_editor(self):
        self.title_screen.hide()
        self.title_form.hide()
        self.show_status("Acquiring character list...")
        self.game_client.get_character_info()
        self.mode = "creator"

    def load_character_selection_screen(self, characters):
        assert self.mode is not None
        _type = self.character_screen_type
        window = self.application_window
        self.character_selection_screen = window.create(_type, mode=self.mode,
                                                        characters=characters)

    def handle_close(self):
        raise SystemExit()

    def select_character(self, character):
        self.game_client.select_character(character.name)
        self.character_selection_screen.delete()
        self.load_initial_window()

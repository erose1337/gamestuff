import os

import pride.gui.gui
import pride.gui.widgetlibrary

class Color_Options_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"method" : "create_color_options", "h_range" : (0, .10),
                "text" : "Color Options", "scale_to_text" : False,
                "tip_bar_text" : "Customize color and design themes"}


class Save_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"method" : "save_character", "h_range" : (0, .10),
                "text" : "Save character", "scale_to_text" : False,
                "tip_bar_text" : "Save the current character to a file"}


class Save_Character_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"method" : "save_and_exit", "h_range" : (0, .10),
                "text" : "Save and continue", "scale_to_text" : False,
                "tip_bar_text" : "Exit back to the title screen"}
    autoreferences = ("game_client", )


class Exit_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"method" : "exit", "h_range" : (0, .10),
                "target" : "/Python",
                "text" : "Exit program", "scale_to_text" : False,
                "tip_bar_text" : "Close the program and return to your desktop"}


class Window_Options_Button(pride.gui.widgetlibrary.Method_Button):

    defaults = {"method" : "create_window_options", "h_range" : (0, .10),
                "text" : "Window Options", "scale_to_text" : False,
                "tip_bar_text" : "Configure resolution and screen settings"}


class Options_Window(pride.gui.gui.Window):

    defaults = {"pack_mode" : "main", "delete_callback" : None,
                "theme_customizer" : None}
    autoreferences = ("theme_customizer", "save_button", "window_customizer")

    def __init__(self, **kwargs):
        super(Options_Window, self).__init__(**kwargs)
        buttons = self.create("pride.gui.gui.Container", pack_mode="top")
        self.buttons = buttons
        buttons.create(Color_Options_Button, target=self.reference)
        buttons.create(Window_Options_Button, target=self.reference)
        buttons.create(Save_Character_Button, target=self.reference)
        buttons.create(Exit_Button)

    def save_and_exit(self):
        self.parent_application.save_character()

    def create_window_options(self):
        if self.window_customizer is not None:
            return
        self.window_customizer = self.create("pride.gui.programs.windowoptions.Window_Options",
                                             delete_callback=self.delete_window_options)
        self.buttons.hide()

    def delete_window_options(self):
        self.buttons.show()

    def create_color_options(self):
        if self.theme_customizer is not None:
            return
        self.theme_customizer = self.create("pride.gui.programs.themecustomizer.Theme_Customizer",
                                            target_theme=self.theme.__class__,
                                            delete_callback=self.delete_color_options)
        self.buttons.hide()

    def delete_color_options(self):
        assert self.delete_callback is None
        #if self.delete_callback is not None:
        #    self.delete_callback()
        self.buttons.show()

    def delete(self):
        self.delete_callback = None
        super(Options_Window, self).delete()

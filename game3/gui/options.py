import os

import pride.gui.gui

import game3.gui.misc


class Options_Window(pride.gui.gui.Window):

    defaults = {"pack_mode" : "main", "delete_callback" : None,
                "theme_customizer" : None}

    def __init__(self, **kwargs):
        super(Options_Window, self).__init__(**kwargs)
        buttons = self.create("pride.gui.gui.Container", pack_mode="top")
        self.buttons = buttons.reference
        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                       method="create_color_options", h_range=(0, .10), text="Color Options",
                       scale_to_text=False)
        #self.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
        #            method="save_state", h_range=(0, .10), text="Save game state",
        #            scale_to_text=False)
        #self.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
        #            method="load_state", h_range=(0, .10), text="Load game state",
        #            scale_to_text=False)
        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                       method="save_character", h_range=(0, .10), text="Save character",
                       scale_to_text=False)
        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                       method="exit_to_title", h_range=(0, .10), text="Exit to title",
                       scale_to_text=False)

    def exit_to_title(self):
        self.parent_application._close_to_title()

    def save_character(self):
        try:
            screen = pride.objects[self.parent_application.character_screen]
        except AttributeError as e:
            pass
        except KeyError:
            pass # show status?
        else:
            screen.save_character()

    def create_color_options(self):
        if self.theme_customizer is not None:
            return
        bar = self.create("pride.gui.gui.Container", h_range=(0, .05), pack_mode="top")
        bar.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                   method="delete_color_options", text='x', pack_mode="right")
        bar.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                   method="export_color_options", text="Export color options",
                   pack_mode="right")
        bar.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
                   method="import_color_options", text="Import color options",
                   pack_mode="right")
        self.bar = bar.reference
        self.theme_customizer = self.create("pride.gui.themecustomizer.Theme_Customizer",
                                            target_theme=self.theme.__class__).reference
        pride.objects[self.buttons].hide()

    def export_color_options(self):
        self._file_selector = self.parent.create("game3.gui.window.File_Selector",
                                                 write_field_method=self._write_color_filename_export).reference
        self.hide()

    def _write_color_filename_export(self, field_name, value):
        self.color_options_file = value
        pride.objects[self._file_selector].delete()
        self.show()
        self._export_color_options()

    def _export_color_options(self):
        self.show_status("Exporting color options...")
        theme = self.theme.__class__.theme_colors
        lines = ["Theme Profiles",
                 '=' * len("Theme Profiles"),
                 '']
        for profile, profile_data in sorted(theme.items()):
            lines.append(profile)
            lines.append('-' * len(profile) + '\n')
            for parameter, value in sorted(profile_data.items()):
                try:
                    r, g, b, a = value
                except TypeError:
                    lines.append("      " + "- {}: {}".format(parameter, value))
                else:
                    lines.append("      " + "- {}: {}".format(parameter, (r, g, b, a)))
            lines.append('\n')

        with open(self.color_options_file, 'w') as _file:
            _file.write('\n'.join(lines))
    #    self.hide_status()

    def import_color_options(self):
        self._file_selector = self.parent.create("game3.gui.window.File_Selector",
                                                 write_field_method=self._write_color_filename_import).reference
        self.hide()

    def _write_color_filename_import(self, field_name, value):
        if not os.path.exists(value):
            return
        self.color_options_file = value
        pride.objects[self._file_selector].delete()
        self.show()
        self._import_color_options()

    def _import_color_options(self):
        game3.gui.misc.set_theme_colors(self, self.color_options_file)
        pride.objects[self.theme_customizer].readjust_sliders()

    def delete_color_options(self):
        pride.objects[self.bar].delete()
        pride.objects[self.theme_customizer].delete()
        self.bar = self.theme_customizer = None
        if self.delete_callback is not None:
            self.delete_callback()
        pride.objects[self.buttons].show()

    #def save_state(self):
    #    self.file_selector = self.create("game3.gui.window.File_Selector",
    #                                     write_field_method=self._save_state).reference

    #def _save_state(self, field_name, value):
    #    pride.objects[self.file_selector].delete()
    #    status = self.create("pride.gui.gui.Container", text="Saving game state...",
    #                         h_range=(0, 80), pack_mode="bottom")
    #    pride.objects[self.sdl_window].run()
    #    app = self.parent_application
    #    with open(value, 'w') as save_file:
    #        state = app.save(save_file)
    #    status.delete()

    def delete(self):
        self.delete_callback = None
        super(Options_Window, self).delete()

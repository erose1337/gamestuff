#initial menu
#------------
#- play
#    - story mode
#    - arcade mode
#- create
#    - create character (freeform, no xp required)
#    - create character (xp budget)
#    - create ability
#- browse (view existing characters/abilities/etc)
#    - characters
#    - abilities
#- customize
#    - window options
#    - color editor
import pride.gui.widgets.formext
import pride.gui.widgets.dbviewer
from pride.gui.widgets.form import field_info
tab_info = pride.gui.widgets.formext.tab_info
Data = pride.gui.widgets.formext.Data

import game3.datatypes

class Story_Menu(Data):

    tab_kwargs = {"button_text" : "Story"}


class Arcade_Menu(Data):

    tab_kwargs = {"button_text" : "Arcade"}


class Play_Menu(Data):

    tab_kwargs = {"button_text" : "Play"}
    tabs = tab_info(story=Story_Menu, arcade=Arcade_Menu)
    ordering = ("story", "arcade")

#----------------------------------------------


class Create_Freeform_Menu(Data):

    # make a Tabbed_Form that targets a new Character
    class Freeform_Editor(pride.gui.widgets.formext.Tabbed_Form):

        # these are assigned before kwargs, which also has target_object set
        #mutable_defaults = {"target_object" : game3.datatypes.Character}
        # so do it this way instead
        def create_subcomponents(self):
            self.target_object = game3.datatypes.Character()
            super(type(self), self).create_subcomponents()

    form_type = Freeform_Editor


class Create_Budgeted_Menu(Data): pass


class Ability_Editor(Data):

    class form_type(pride.gui.widgets.formext.Tabbed_Form):

        def create_subcomponents(self):
            self.target_object = ability = game3.datatypes.Ability()
            create_ability_menu = self.parent.parent.target_object
            options = create_ability_menu.options
            options.target_ability = ability
            super(type(self), self).create_subcomponents()
            options.editor_form = ability.form_reference


class Ability_Options_Menu(Data):

    defaults = {"resources_reference" :\
                      "/Python/SDL_Window/Game_Window/Game3_Client_Resources", }

    fields = [[field_info("save_ability", button_text="Save",
                          entry_kwargs={"scale_to_text" : False})],
              [field_info("reset_ability", button_text="Reset",
                          entry_kwargs={"scale_to_text" : False})]]
    form_kwargs = {"h_range" : (0, .1)}
    autoreferences = ("target_ability", )

    def save_ability(self):
        ability = self.target_ability
        resources = pride.objects[self.resources_reference]
        resources.add_ability(ability)
        pride.objects[self.editor_form].show_status("Saved ability")

    def reset_ability(self):
        ability = self.target_ability
        for key in ("name", "homing", "passive", "range", "target_count",
                    "aoe", "no_cost", "tree", "energy_source",
                    "influence", "element", "magnitude",
                    "duration", "effect_type", "trigger", "target", "reaction"):
            setattr(ability, key, ability.defaults[key])
        form = pride.objects[self.editor_form]
        form.synchronize_fields()
        form.show_status("Reset ability fields to defaults")


class Create_Ability_Menu(Data):

    tabs = tab_info(editor=Ability_Editor, options=Ability_Options_Menu)
    ordering = ("editor", "options")

    #def setup_tabs(self, tabs):
    #    super(Create_Ability_Menu, self).setup_tabs(tabs)
    #    print self.editor, dir(self.editor)
    #    ability = pride.objects[self.editor.form_reference].target_object
    #    self.options.target_ability = ability


class Create_Menu(Data):

    tab_kwargs = {"button_text" : "Create"}
    tabs = tab_info(freeform=Create_Freeform_Menu,
                    budgeted=Create_Budgeted_Menu,
                    ability=Create_Ability_Menu)
    ordering = ("freeform", "budgeted", "ability")


class Browse_Freeform_Menu(Data): pass
class Browse_Budgeted_Menu(Data): pass
class Browse_Abilities_Menu(Data):

    tab_kwargs = {"button_text" : "Browse Abilities"}



class Browse_Menu(Data):

    tab_kwargs = {"button_text" : "Browse"}
    #tabs = tab_info(browse_freeform=Browse_Freeform_Menu,
    #                browse_budgeted=Browse_Budgeted_Menu,
    #                browse_abilities=Browse_Abilities_Menu)
    #ordering = ("browse_freeform", "browse_budgeted", "browse_abilities")

    class form_type(pride.gui.widgets.dbviewer.Db_Viewer):

        defaults = {"read_only" : True}

        def create_subcomponents(self):
            reference = "/Python/SDL_Window/Game_Window/Game3_Client_Resources"
            self.db = pride.objects[reference]
            super(type(self), self).create_subcomponents()



class Window_Options_Menu(Data): pass
class Color_Editor_Menu(Data): pass

class Customize_Menu(Data):

    tab_kwargs = {"button_text" : "Customize"}
    tabs = tab_info(window_options=Window_Options_Menu,
                    color_editor=Color_Editor_Menu)
    ordering = ("window_options", "color_editor")


class Game_Menu(Data):

    tabs = tab_info(play_menu=Play_Menu, create_menu=Create_Menu,
                    browse_menu=Browse_Menu, customize_menu=Customize_Menu)
    ordering = ("play_menu", "create_menu", "browse_menu", "customize_menu")

#Game_Menu = Data.from_info("Game_Menu", # name
#                           ("play_menu", "create_menu",
#                            "browse_menu", "customize_menu"), # tabs
#                           ("game3.gui.window3.Play_Menu",         #
#                            "game3.gui.window3.Create_Menu",       # Data types
#                            "game3.gui.window3.Browse_Menu",       #
#                            "game3.gui.window3.Customize_Menu"))


class Game_Window(pride.gui.widgets.formext.Tabbed_Form):

    mutable_defaults = {"target_object" : Game_Menu}
    defaults = {"main_window_type" : "game3.gui.stars.Star_Background"}

    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        resources = self.create("game3.engine.resources.Game3_Client_Resources")
        self.remove(resources)


def test_Game_Window():
    import pride
    import pride.gui
    import pride.gui.main
    import game3.rules
    game3.rules.set_rules()
    window = pride.objects[pride.gui.enable(position=(100, 100))]
    window.create(pride.gui.main.Gui, startup_programs=(Game_Window, ),
                  user=pride.objects["/User"])

if __name__ == "__main__":
    test_Game_Window()

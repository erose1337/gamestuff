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

import game3.datatypes

class Story_Menu(pride.gui.widgets.formext.Data):

    tab_kwargs = {"button_text" : "Story"}


class Arcade_Menu(pride.gui.widgets.formext.Data):

    tab_kwargs = {"button_text" : "Arcade"}


class Play_Menu(pride.gui.widgets.formext.Data):

    tabs = ("story", "arcade")
    tab_kwargs = {"button_text" : "Play"}
    mutable_defaults = {"story" : Story_Menu, "arcade" : Arcade_Menu}


class Create_Freeform_Menu(pride.gui.widgets.formext.Data):

    # make a Tabbed_Form that targets a new Character
    class Freeform_Editor(pride.gui.widgets.formext.Tabbed_Form):

        # these are assigned before kwargs, which also has target_object set
        #mutable_defaults = {"target_object" : game3.datatypes.Character}
        # so do it this way instead
        def create_subcomponents(self):
            self.target_object = game3.datatypes.Character()
            super(type(self), self).create_subcomponents()


    form_type = Freeform_Editor


class Create_Budgeted_Menu(pride.gui.widgets.formext.Data): pass
class Create_Ability_Menu(pride.gui.widgets.formext.Data): pass


class Create_Menu(pride.gui.widgets.formext.Data):

    tabs = ("freeform", "budgeted", "ability")
    tab_kwargs = {"button_text" : "Create"}
    mutable_defaults = {"freeform" : Create_Freeform_Menu,
                        "budgeted" : Create_Budgeted_Menu,
                        "ability" : Create_Ability_Menu}

class Browse_Freeform_Menu(pride.gui.widgets.formext.Data): pass
class Browse_Budgeted_Menu(pride.gui.widgets.formext.Data): pass
class Browse_Abilities_Menu(pride.gui.widgets.formext.Data): pass

class Browse_Menu(pride.gui.widgets.formext.Data):

    tabs = ("browse_freeform", "browse_budgeted", "browse_abilities")
    tab_kwargs = {"button_text" : "Browse"}
    mutable_defaults = {"browse_freeform" : Browse_Freeform_Menu,
                        "browse_budgeted" : Browse_Budgeted_Menu,
                        "browse_abilities" : Browse_Abilities_Menu}


class Window_Options_Menu(pride.gui.widgets.formext.Data): pass
class Color_Editor_Menu(pride.gui.widgets.formext.Data): pass

class Customize_Menu(pride.gui.widgets.formext.Data):

    tabs = ("window_options", "color_editor")
    tab_kwargs = {"button_text" : "Customize"}
    mutable_defaults = {"window_options" : Window_Options_Menu,
                        "color_editor" : Color_Editor_Menu}


class Game_Menu(pride.gui.widgets.formext.Data):

    tabs = ("play_menu", "create_menu", "browse_menu", "customize_menu")
    mutable_defaults = {"play_menu" : Play_Menu, "create_menu" : Create_Menu,
                        "browse_menu" : Browse_Menu,
                        "customize_menu" : Customize_Menu}


class Game_Window(pride.gui.widgets.formext.Tabbed_Form):

    mutable_defaults = {"target_object" : Game_Menu}


def test_Game_Window():
    import pride
    import pride.gui
    import pride.gui.main
    import game3.rules
    game3.rules.set_rules()
    window = pride.objects[pride.gui.enable()]
    window.create(pride.gui.main.Gui, startup_programs=(Game_Window, ),
                  user=pride.objects["/User"])

if __name__ == "__main__":
    test_Game_Window()

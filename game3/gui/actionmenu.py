import pride.gui.gui
import pride.gui.widgetlibrary

import game3.abilities

class Displayer(pride.gui.gui.Container):

    defaults = {"attribute" : '', "_object" : None}
    required_attributes = ("attribute", "_object")

    def __init__(self, **kwargs):
        super(Displayer, self).__init__(**kwargs)
        attribute = self.attribute
        self.create("pride.gui.gui.Container", text=attribute, pack_mode="left",
                    scale_to_text=True)
        self.create("pride.gui.gui.Container", text=str(getattr(self._object, attribute)),
                    pack_mode="left")


class Ability_Fields(pride.gui.gui.Container):

    defaults = {"tab" : '', "character" : None, "ability" : None, "tree" : ''}
    required_attributes = ("character", "ability")

    def _get_active_or_passive(self):
        if isinstance(self.ability, game3.abilities.Active_Ability):
            return "Active"
        else:
            return "Passive"
    active_or_passive = property(_get_active_or_passive)

    def _get_energy_cost(self):
        return self.ability.calculate_ability_cost(self.character, None)
    energy_cost = property(_get_energy_cost)

    def __init__(self, **kwargs):
        super(Ability_Fields, self).__init__(**kwargs)
        ability = self.ability
        # name, xp cost energy cost
        # active/passive, range, target count, aoe
        # effects
        row1 = self.create("pride.gui.gui.Container")
        for attribute in ("target_count", "aoe", "range"):
            row1.create(Displayer, attribute=attribute, _object=ability)
        row2 = self.create("pride.gui.gui.Container")
        row2.create(Displayer, attribute="homing", _object=ability)
        row2.create(Displayer, attribute="energy_cost", _object=self)
        row2.create(Displayer, attribute="active_or_passive", _object=self)

        #self.effects_window = self.create(Effect_Selection_Window, ability=ability,


class Ability_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed Ability", "editable" : False}


class Ability_Selection_Window(pride.gui.widgetlibrary.Tabbed_Window):

    defaults = {"tab_type" : Ability_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Abilities", "window_type" : Ability_Fields,
                "character" : '', "tree" : ''}
    required_attributes = ("character", "tree")

    def __init__(self, **kwargs):
        super(Ability_Selection_Window, self).__init__(**kwargs)
        tree = self.tree
        for ability_name in tree.abilities:
            tab_kwargs = {"text" : ability_name}
            window_kwargs = {"ability" : getattr(tree, ability_name),
                             "tree" : tree.reference}
            self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        assert window_kwargs["ability"].name in self.tree.abilities, (window_kwargs["ability"].name, self.tree.abilities)
        window_kwargs.update({"character" : self.character})
        super(Ability_Selection_Window, self).new_tab(window_kwargs, tab_kwargs)


class Ability_Tree_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed Ability Tree", "editable" : False}


class Abilities_Viewer(pride.gui.widgetlibrary.Tab_Switching_Window):

    defaults = {"tab_type" : Ability_Tree_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Ability Trees", "window_type" : Ability_Selection_Window,
                "character" : ''}
    required_attributes = ("character", )

    def initialize_tabs_and_windows(self):
        tab_bar = self.create(self.tab_bar_type, label=self.tab_bar_label,
                              tab_types=self.tab_types)
        self.tab_bar = tab_bar.reference
        tree_names = [tree for tree in self.character.abilities]
        if tree_names:
            window_types = []
            window_type = self.window_type
            for ability_tree in tree_names:
                tab_bar.new_tab(scale_to_text=False)
                window_types.append(window_type)
            self.window_types = window_types
            self.create_windows()

    def create_windows(self):
        tabs = pride.objects[self.tab_bar].tabs
        abilities = self.character.abilities
        tree_names = list(abilities)
        for index, window_type in reversed(list(enumerate(self.window_types))):
            window = self.create(window_type, tab=tabs[index],
                                 character=self.character,
                                 tree=getattr(abilities, tree_names[index]))
            tab = pride.objects[tabs[index]]
            tab.window = window.reference
            if index:
                window.hide()
                pride.objects[tab.indicator].disable_indicator()
            else:
                pride.objects[tab.indicator].enable_indicator()

    #def __init__(self, **kwargs):
    #    super(Abilities_Viewer, self).__init__(**kwargs)
    #    _abilities = self.character.abilities
    #    for ability_tree in _abilities.ability_trees:
    #        if ability_tree == "Misc":
    #            continue
    #        tab_kwargs = {"text" : ability_tree}
    #        window_kwargs = {"tree" : getattr(_abilities, ability_tree)}
    #        self.new_tab(window_kwargs, tab_kwargs)

    #def new_tab(self, window_kwargs=None, tab_kwargs=None):
    #    assert window_kwargs["tree"].name in self.character.abilities
    #    window_kwargs.update({"character" : self.character})
    #    super(Abilities_Viewer, self).new_tab(window_kwargs, tab_kwargs)


class Status_Window(pride.gui.gui.Container):

    def add_text(self, text):
        self.text += '\n' + text


class Action_Menu(pride.gui.widgetlibrary.Tab_Switching_Window):

    defaults = {"tab_types" : tuple(pride.gui.widgetlibrary.Tab_Button.from_info(text=text, include_delete_button=False)
                                    for text in ("Abilities", "Status")),
                "window_types" : (Abilities_Viewer, Status_Window),
                "character" : ''}

    def create_windows(self):
        abilities_tab, status_tab = pride.objects[self.tab_bar].tabs
        abilities_window = self.create(self.window_types[0], tab=abilities_tab,
                                       character=self.character)
        status_window = self.create(self.window_types[1], tab=status_tab,
                                    character=self.character)
        abilities_window.hide()
        status_window.show()

        abilities_tab = pride.objects[abilities_tab]
        abilities_tab.window = abilities_window.reference
        pride.objects[abilities_tab.indicator].enable_indicator()

        status_tab = pride.objects[status_tab]
        status_tab.window = status_window.reference

        self.status_window = status_window.reference

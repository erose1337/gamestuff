import pride.gui.gui
import pride.gui.widgets.tabs

import game3.abilities
import game3.elements

class Displayer(pride.gui.gui.Container):

    defaults = {"attribute" : '', "_object" : None, "pack_mode" : "left"}
    required_attributes = ("attribute", "_object")

    def __init__(self, **kwargs):
        super(Displayer, self).__init__(**kwargs)
        attribute = self.attribute
        self.create("pride.gui.gui.Container", text=attribute.replace('_', ' '),
                    pack_mode="top", scale_to_text=False)
        self.create("pride.gui.gui.Button", text=str(getattr(self._object, attribute)),
                    pack_mode="bottom")


class Effect_Fields(pride.gui.gui.Container):

    defaults = {"tab" : '', "effect" : None}
    required_attributes = ("effect", )

    def __init__(self, **kwargs):
        super(Effect_Fields, self).__init__(**kwargs)
        effect = self.effect()
        # effect type   influence    element
        # Magnitude   duration  reaction
        # triggered     reaction targets
        row1 = self.create("pride.gui.gui.Container")
        for attribute in ("type_name", "influence"):
            row1.create(Displayer, attribute=attribute, _object=effect)
        if effect.type_name == "damage":
            row1.create(Displayer, attribute="element", _object=effect)

        row2 = self.create("pride.gui.gui.Container")
        for attribute in ("magnitude", "duration", "reaction"):
            row2.create(Displayer, attribute=attribute, _object=effect)
        if effect.reaction:
            row3 = self.create("pride.gui.gui.Container")
            for attribute in ("trigger", "target"):
                row3.create(Displayer, attribute=attribute, _object=effect)


class Effect_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Effect", "editable" : False,
                "include_delete_button" : False}


class Effect_Selection_Window(pride.gui.widgets.tabs.Tab_Switching_Window):

    defaults = {"tab_type" : Effect_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Effects", "window_type" : Effect_Fields,
                "ability" : '', "include_delete_button" : False}
    required_attributes = ("ability", )

    def initialize_tabs_and_windows(self):
        tab_type = self.tab_type.from_info
        self.tab_types = [tab_type(text=effect.defaults["name"]) for effect in self.ability.effects]
        self.tab_bar = self.create(self.tab_bar_type, label=self.tab_bar_label,
                                   tab_types=self.tab_types)
        self.create_windows()

    def create_windows(self):
        tabs = self.tab_bar.tabs
        window_type = self.window_type
        ability = self.ability
        _effects = ability.effects
        for index, tab in reversed(list(enumerate(tabs))):
            window = self.create(window_type, effect=_effects[index], tab=tab)
            tab.window = window
            if index:
                window.hide()
                tab.indicator.disable_indicator()
            else:
                tab.indicator.enable_indicator()


class Ability_Fields(pride.gui.gui.Container):

    defaults = {"tab" : '', "character" : None, "ability" : None}
    required_attributes = ("character", "ability")
    autoreferences = ("effects_window", )

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
        _ability_info = self.create("pride.gui.gui.Container")
        row1 = _ability_info.create("pride.gui.gui.Container")
        for attribute in ("target_count", "aoe", "range"):
            row1.create(Displayer, attribute=attribute, _object=ability)
        row2 = _ability_info.create("pride.gui.gui.Container")
        row2.create(Displayer, attribute="homing", _object=ability)
        row2.create(Displayer, attribute="energy_cost", _object=self)
        row2.create(Displayer, attribute="active_or_passive", _object=self)

        self.effects_window = self.create(Effect_Selection_Window, ability=ability)


class Ability_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Ability", "editable" : False,
                "include_delete_button" : False}

    def select(self, mouse):
        super(Ability_Tab, self).select(mouse)
        self.parent_application.select_ability(self.window.ability)


class Ability_Selection_Window(pride.gui.widgets.tabs.Tab_Switching_Window):

    defaults = {"tab_type" : Ability_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Abilities", "window_type" : Ability_Fields,
                "character" : '', "tree" : '', "include_delete_button" : False,
                }
    required_attributes = ("character", "tree")

    def initialize_tabs_and_windows(self):
        tree = self.tree
        ability_names = list(tree.abilities)
        tab_type = self.tab_type.from_info
        self.tab_types = [tab_type(text=name) for name in ability_names]
        self.tab_bar = self.create(self.tab_bar_type, label=self.tab_bar_label,
                                   tab_types=self.tab_types)
        self.create_windows()

    def create_windows(self):
        tabs = self.tab_bar.tabs
        window_type = self.window_type
        _abilities = [getattr(self.tree, name) for name in self.tree.abilities]
        _character = self.character
        for index, tab in reversed(list(enumerate(tabs))):
            window = self.create(window_type, ability=_abilities[index], tab=tab,
                                 character=_character)
            tab.window = window
            if index:
                window.hide()
                tab.indicator.disable_indicator()
            else:
                tab.indicator.enable_indicator()


class Ability_Tree_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Ability Tree", "editable" : False,
                "include_delete_button" : False,
                "tip_bar_text" : "View ability information"}


class Abilities_Viewer(pride.gui.widgets.tabs.Tab_Switching_Window):

    defaults = {"tab_type" : Ability_Tree_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Ability Trees", "window_type" : Ability_Selection_Window,
                "character" : ''}
    required_attributes = ("character", )

    def initialize_tabs_and_windows(self):
        tab_bar = self.create(self.tab_bar_type, label=self.tab_bar_label,
                              tab_types=self.tab_types)
        self.tab_bar = tab_bar
        tree_names = [tree for tree in self.character.abilities]
        if tree_names:
            window_types = []
            window_type = self.window_type
            for ability_tree in tree_names:
                tab_bar.new_tab(scale_to_text=False, text=ability_tree,
                                include_delete_button=False)
                window_types.append(window_type)
            self.window_types = window_types
            self.create_windows()

    def create_windows(self):
        tabs = self.tab_bar.tabs
        abilities = self.character.abilities
        tree_names = list(abilities)
        for index, window_type in reversed(list(enumerate(self.window_types))):
            window = self.create(window_type, tab=tabs[index],
                                 character=self.character,
                                 tree=getattr(abilities, tree_names[index]))
            tab = tabs[index]
            tab.window = window
            if index:
                window.hide()
                tab.indicator.disable_indicator()
            else:
                tab.indicator.enable_indicator()


class Status_Window(pride.gui.gui.Container):

    def add_text(self, text):
        self.text += '\n' + text


class Attributes_Displayer(pride.gui.gui.Container):

    defaults = {"_object" : None, "entries_per_column" : 3}
    mutable_defaults = {"attribute_listing" : dict}
    required_attributes = ("attribute_listing", )

    def __init__(self, **kwargs):
        super(Attributes_Displayer, self).__init__(**kwargs)
        self.create_attribute_fields()

    def create_attribute_fields(self):
        try:
            for category, attributes in sorted(self.attribute_listing.items()):
                self._create_column(category, attributes)
        except AttributeError:
            if hasattr(self.attribute_listing, "items"):
                raise
            for attributes in pride.functions.utilities.slide(self.attribute_listing,
                                                              self.entries_per_column):
                self._create_column('', attributes)

    def _create_column(self, column_name, column_attributes):
        _object = self._object
        column = self.create("pride.gui.gui.Container", pack_mode="left")
        if column_name:
            column.create("pride.gui.gui.Container", text=column_name,
                        pack_mode="top", h_range=(0, 40))
        for attribute in column_attributes:
            initial_value = str(getattr(_object, attribute))
            column.create(Displayer, attribute=attribute.replace('_', ' '),
                          _object=_object, pack_mode="top")


class Attributes_Viewer(Attributes_Displayer):

    mutable_defaults = {"attribute_listing" : lambda: {"health" : ("toughness", "regeneration", "soak"),
                                                       "energy" : ("willpower", "recovery", "grace"),
                                                       "movement" : ("mobility", "recuperation", "conditioning")}}

    def create_attribute_fields(self):
        self._object = self.character.attributes
        super(Attributes_Viewer, self).create_attribute_fields()


class Affinities_Viewer(Attributes_Displayer):

    defaults = {"attribute_listing" : game3.elements.ELEMENTS}

    def create_attribute_fields(self):
        self._object = self.character.affinities
        super(Affinities_Viewer, self).create_attribute_fields()


class Accept_Button(pride.gui.gui.Button):

    defaults = {"text" : "Accept", "scale_to_text" : True,
                "tip_bar_text" : "Accept the current action and proceed with the turn"}

    def left_click(self, mouse):
        self.parent_application.accept_action()


class Action_Menu(pride.gui.widgets.tabs.Tab_Switching_Window):

    generator = (pride.gui.widgets.tabs.Tab_Button.from_info(text=text,
                                                              include_delete_button=False,
                                                              tip_bar_text=tip)
                 for text, tip in (("Abilities", "Examine and select an ability"),
                                   ("Attributes", "Examine attributes"),
                                   ("Affinities", "Examine affinities"),
                                   ("Status", "A transcript of past actions and current state")))
    defaults = {"tab_types" : tuple(generator),
                "window_types" : (Abilities_Viewer, Attributes_Viewer,
                                  Affinities_Viewer, Status_Window),
                "character" : ''}
    del generator
    autoreferences = ("status_indicator", )

    def initialize_tabs_and_windows(self):
        bar = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        self.tab_bar = bar.create(self.tab_bar_type, label=self.tab_bar_label,
                                   tab_types=self.tab_types, pack_mode="left")
        bar.create(Accept_Button, pack_mode="left")
        self.status_indicator = self.create("game3.gui.charactersheet.Status_Indicator",
                                            character=self.character)
        self.create_windows()

    def create_windows(self):
        _character = self.character
        for tab, window_type in reversed(zip(self.tab_bar.tabs, self.window_types)):
            window = self.create(window_type, tab=tab, character=_character)
            setattr(self, window_type.__name__.lower(), window)
            tab.window = window
            window.hide()
        window.show()
        tab.indicator.enable_indicator()

    def delete(self):
        for window_type in self.window_types:
            setattr(self, window_type, None)
        super(Action_Menu, self).delete()

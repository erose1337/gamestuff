import pride.gui.gui
import pride.gui.widgetlibrary
import pride.gui.widgets.tabs
import pride.gui.widgets.form
from pride.functions.utilities import slide

import attributes
import affinities
import abilities
import effects
import elements
import game3.rules


class Name_Field(pride.gui.widgetlibrary.Field):

    defaults = {"field_name" : "Name", "initial_value" : '',
                "tip_bar_text" : "Enter a name here"}


class Attribute_Fields(pride.gui.widgets.form.Form):

    defaults = {"form_name" : "Attributes", "include_balance_display" : False,
                "tip_bar_text" : game3.attributes.ATTRIBUTE_DESCRIPTION}
    fields = []
    for triplet in (("toughness", "willpower", "mobility"),
                    ("regeneration", "recovery", "recuperation"),
                    ("soak", "grace", "conditioning")):
        description = [{"tip_bar_text" : attributes.Attributes.description[item],
                        "minimum" : 0, "maximum" : 255} for item in triplet]
        fields.append(zip(triplet, description))
    defaults["fields"] = fields
    del fields


class Affinity_Fields(pride.gui.widgets.form.Form):

    defaults = {"form_name" : "Affinities", "include_balance_display" : False,
                "fields" : [list(three_elements) for three_elements in
                            slide(game3.elements.ELEMENTS, 3)],
                "tip_bar_text" : game3.affinities.AFFINITY_DESCRIPTION}


class XP_Cost_Indicator(pride.gui.gui.Container):

    autoreferences = ("display", )

    def __init__(self, **kwargs):
        super(XP_Cost_Indicator, self).__init__(**kwargs)
        self.create("pride.gui.gui.Container", text="XP cost")
        self.display = self.create("pride.gui.gui.Container", text='0')


class Energy_Cost_Indicator(pride.gui.gui.Container):

    defaults = {"pack_mode" : "left", "w_range" : (0, 120)}
    autoreferences = ("display", )

    def __init__(self, **kwargs):
        super(Energy_Cost_Indicator, self).__init__(**kwargs)
        self.create("pride.gui.gui.Container", text="energy cost")
        self.display = self.create("pride.gui.gui.Container", text='0')


class Active_Passive_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Active or Passive:", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("Active", "Passive")),
                "pack_mode" : "left", "ability_fields" : ''}
    autoreferences = ("ability_fields", )

    def on_dropdown_selection(self, selection):
        ability_fields = self.ability_fields
        if selection == "Active":
            if ability_fields.active_or_passive != "Active":
                ability_fields.active_or_passive = "Active"
                for effect_fields in ability_fields.effects_window.window_listing:
                    effect_fields.update_values(duration=0)
                    duration_field = effect_fields.duration_field
                    duration_field.field.text = '0'
                ability_fields.update_costs()
        else:
            assert selection == "Passive"
            if ability_fields.active_or_passive != "Passive":
                ability_fields.active_or_passive = "Passive"
                ability_fields.update_values(range="self", target_count=1)

                for effect_fields in ability_fields.effects_window.window_listing:
                    effect_fields.update_values(duration=0)
                    effect_fields.duration_field.field.text = "passive"

                ability_fields.range_field.field.text = "self"
                ability_fields.target_count_field.field.text = '1'


class Homing_Type_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Homing", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("True", "False")),
                "ability_fields" : '', "pack_mode" : "left",
                "w_range" : (0, 120)}
    autoreferences = ("ability_fields", )

    def on_dropdown_selection(self, selection):
        if selection == "True":
            value = True
        else:
            value = False
        self.ability_fields.update_values(homing=value)


class Effect_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Effect"}


class Range_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Range",
                "initial_value" : "self", "ability_fields" : ''}
    required_attributes = ("ability_fields", )
    autoreferences = ("ability_fields", )

    def on_increment(self, current_value):
        if self.ability_fields.active_or_passive == "Passive":
            return "self"
        if current_value == "self":
            new_value = 0
        else:
            new_value = int(current_value) + 1
        self.ability_fields.update_values(range=new_value)
        return new_value

    def on_decrement(self, current_value):
        if current_value == "self":
            return "self"
        else:
            new_value = int(current_value) - 1
            changes = dict()
            ability_fields = self.ability_fields
            if new_value == -1:
                new_value = "self"
                changes["target_count"] = 1
                ability_fields.target_count_field.field.text = '1'
            changes["range"] = new_value
            ability_fields.update_values(**changes)
            return new_value


class Aoe_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "AoE", "initial_value" : '1',
                "ability_fields" : ''}
    autoreferences = ("ability_fields", )

    def on_increment(self, current_value):
        new_value = int(current_value) + 1
        self.ability_fields.update_values(aoe=new_value)
        return new_value

    def on_decrement(self, current_value):
        new_value = int(current_value) - 1
        if new_value > 0:
            self.ability_fields.update_values(aoe=new_value)
        else:
            new_value += 1
        return new_value


class Target_Count_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Target count",
                "initial_value" : '1', "ability_fields" : ''}
    autoreferences = ("ability_fields", )

    def on_increment(self, current_value):
        ability_fields = self.ability_fields
        if ability_fields.active_or_passive == "Active" and ability_fields.ability.range != "self":
            new_value = int(current_value) + 1
        else:
            new_value = 1
        ability_fields.update_values(target_count=new_value)
        return new_value

    def on_decrement(self, current_value):
        current_value = int(current_value)
        ability_fields = self.ability_fields
        if ability_fields.active_or_passive == "Active":
            if current_value > 1:
                new_value = current_value - 1
                ability_fields.update_values(target_count=new_value)
                return new_value
        return current_value


class Ability_Fields(pride.gui.gui.Container):

    defaults = {"tab" : '', "character" : None, "active_or_passive" : "Active",
                "character_screen" : '', "_old_xp_cost" : 0, "ability" : None,
                "tree" : ''}
    required_attributes = ("character", "character_screen", "ability")
    autoreferences = ("xp_cost_indicator", "energy_cost_indicator",
                      "homing_selector", "active_passive_selector",
                      "range_field", "target_count_field", "effects_window",
                      "tree", "character_screen", "tab")

    def __init__(self, **kwargs):
        super(Ability_Fields, self).__init__(**kwargs)
        ability = self.ability
        # name, xp cost energy cost
        # active/passive, range, target count, aoe
        # effects
        row1 = self.create("pride.gui.gui.Container", h_range=(0, 40))
        row1.create(Name_Field, pack_mode="left", initial_value=ability.name,
                    write_field_method=self._write_ability_name)
        self.xp_cost_indicator = row1.create(XP_Cost_Indicator, pack_mode="left", w_range=(0, 120))
        self.energy_cost_indicator = row1.create(Energy_Cost_Indicator)
        self.homing_selector = row1.create(Homing_Type_Selector, initial_value=ability.homing,
                                           ability_fields=self)

        row2 = self.create("pride.gui.gui.Container", h_range=(0, 40))
        if isinstance(ability, abilities.Active_Ability):
            self.active_or_passive = "Active"
        else:
            self.active_or_passive = "Passive"
        self.active_passive_selector = row2.create(Active_Passive_Selector, initial_value=self.active_or_passive,
                                                   ability_fields=self)
        self.range_field = row2.create(Range_Field, initial_value=ability.range,
                                       ability_fields=self)
        self.target_count_field = row2.create(Target_Count_Field, initial_value=ability.target_count,
                                              ability_fields=self)
        row2.create(Aoe_Field,initial_value=ability.aoe, ability_fields=self)

        self.effects_window = self.create(Effect_Selection_Window, ability=ability,
                                          ability_fields=self)
        assert self.tree
        self.update_costs()

    def update_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.ability, key, value)
        self.update_costs()

    def update_costs(self):
        ability = self.ability
        if len(ability.effects) > 1 and effects.Null in ability.effects:
            self.ability.remove_effect(effects.Null)
        kwargs = {"name" : ability.name, "range" : ability.range, "effects" : ability.effects,
                  "target_count" : ability.target_count, "aoe" : ability.aoe,
                  "homing" : ability.homing}
        if self.active_passive_selector.selection == "Active":
            if not isinstance(ability, abilities.Active_Ability):
                ability = abilities.Active_Ability.from_info(**kwargs)
        else:
            if not isinstance(ability, abilities.Passive_Ability):
                ability = abilities.Passive_Ability.from_info(**kwargs)

        tree = self.tree
        tree.remove_ability(self.ability)
        self.ability = ability
        tree.add_ability(ability)
        energy_cost = ability.calculate_ability_cost(self.character, None)
        self.energy_cost_indicator.display.text = str(energy_cost)

        character_screen = self.character_screen
        xp_cost = game3.rules.calculate_ability_acquisition_cost(self.character, ability)
        character_screen._modify_xp(self._old_xp_cost)
        character_screen._modify_xp(-xp_cost)
        self._old_xp_cost = xp_cost
        self.xp_cost_indicator.display.text = str(xp_cost)

    def _write_ability_name(self, field_name, name):
        tab = self.tab
        tab.text = name
        tab.deselect(None, None) # sets ability name, among other things
        self.pack() # because of scale_to_text

    def delete(self):
        self.character_screen._modify_xp(self._old_xp_cost)
        del self.character
        del self.ability
        super(Ability_Fields, self).delete()

    def add_effect(self, effect_type):
        self.ability.add_effect(effect_type)

    def remove_effect(self, effect_type):
        self.ability.remove_effect(effect_type)


class Trigger_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "trigger", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(trigger)
                                      for trigger in ("Damage", "Heal", "Buff", "Debuff")),
                "effect_fields" : '', "pack_mode" : "left"}
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(trigger=selection)


class Effect_Type_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Effect type", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("Damage", "Heal", "Buff", "Debuff",
                                                    "Movement")),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        effect_fields = self.effect_fields
        effect = effect_fields.effect
        self.remove_old_effect(effect_fields, effect)

        info = effect.defaults
        kwargs = {"name" : info["name"], "influence" : info["influence"],
                  "magnitude" : info["magnitude"], "duration" : info["duration"]}

        self.toggle_element_selector(selection, effect_fields, kwargs)
        selector = effect_fields.influence_selector

        if selection in ("Damage", "Heal"):
            self.select_damage_heal(selector, effect_fields, kwargs)
        elif selection in ("Buff", "Debuff"):
            self.select_buff_debuff(selector, effect_fields, kwargs)
        else:
            assert selection == "Movement"
            self.select_movement(selector, effect_fields, kwargs)

        effect = effect_fields.effect = getattr(effects, selection).from_info(**kwargs)
        self.add_new_effect(effect_fields, effect)

    def add_new_effect(self, effect_fields, effect):
        ability_fields = effect_fields.ability_fields
        ability_fields.add_effect(effect)
        ability_fields.update_costs()

    def remove_old_effect(self, effect_fields, effect):
        ability_fields = effect_fields.ability_fields
        ability_fields.remove_effect(effect)

    def toggle_element_selector(self, selection, effect_fields, kwargs):
        if selection != "Damage":
            if effect_fields.element_selector is not None:
                effect_fields.element_selector.delete()
                effect_fields.element_selector = None
        else:
            if effect_fields.element_selector is None:
                row2 = effect_fields.row2
                effect_fields.element_selector = row2.create(Element_Selector, effect_fields=effect_fields)
            kwargs["element"] = effect_fields.element_selector.selection

    def _select_type(self, selector, effect_fields, kwargs, selector_type):
        if not isinstance(selector, selector_type):
            row = selector.parent
            selector.delete()
            selector = row.create(selector_type, effect_fields=effect_fields)
            effect_fields.influence_selector = selector
        kwargs["influence"] = selector.selection
        return selector

    def select_damage_heal(self, selector, effect_fields, kwargs):
        self._select_type(selector, effect_fields, kwargs, Influence_Selector_Permanent)

    def select_buff_debuff(self, selector, effect_fields, kwargs):
        self._select_type(selector, effect_fields, kwargs, Influence_Selector_Temporary)

    def select_movement(self, selector, effect_fields, kwargs):
        self._select_type(selector, effect_fields, kwargs, Influence_Selector_Position)


class Influence_Selector_Permanent(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : tuple([pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(stat) for
                                       stat in ("health", "energy", "movement")]),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(influence=selection)


class Influence_Selector_Temporary(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : tuple([pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(influence, "attributes.{}".format(influence))
                                       for influence in attributes.Attributes.attributes]),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(influence=selection)


class Influence_Selector_Position(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : (pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info("position"), ),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(influence=selection)


class Influence_Selector_Null(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : (pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info("----", selection_value="null"), ),
                "effect_fields" : '', "pack_mode" : "left"}

    def on_dropdown_selection(self, selection):
        pass


class Reaction_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Reaction", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(choice)
                                      for choice in ("False", "True")),
                "effect_fields" : '', "pack_mode" : "left"}
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        effect_fields = self.effect_fields
        update_info = False
        if selection == "True":
            effect_fields.open_reactions()
            if not effect_fields.effect.defaults["reaction"]:
                update_info = True
                effect_type = effect_fields.effect_type_selector.selection
                new_effect = getattr(effects, effect_type).from_info(**effect_fields.effect.defaults)
        else:
            effect_fields.close_reactions()
            if effect_fields.effect.defaults["reaction"]:
                update_info = True
                effect_type = effect_fields.effect_type_selector.selection
                new_effect = getattr(effects, effect_type).from_info(**effect_fields.effect.defaults)

        if update_info:
            if selection == "True":
                kwargs = {"reaction" : True, "trigger" : effect_fields.trigger_selector.selection,
                          "target" : effect_fields.reaction_target_selector.selection}
            else:
                kwargs = {"reaction" : False}
            effect_fields.remove_effect(effect_fields.effect)
            ability_fields = effect_fields.ability_fields
            ability_fields.ability.remove_effect(effect_fields.effect)
            effect_fields.effect = new_effect
            ability_fields.ability.add_effect(new_effect)
            effect_fields.update_values(**kwargs)


class Reaction_Target_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Reaction target", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(target)
                                      for target in ("reacting actor", "triggering actor")),
                "pack_mode" : "left"}
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(target=selection)


class Element_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Element", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(element)
                                      for element in elements.ELEMENTS),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        self.effect_fields.update_values(element=selection)


class Magnitude_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Magnitude",
                "initial_value" : '1', "effect_fields" : ''}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_increment(self, current_value):
        new_value = int(current_value) + 1
        self.effect_fields.update_values(magnitude=new_value)
        return new_value

    def on_decrement(self, current_value):
        new_value = int(current_value) - 1
        if new_value > 0:
            self.effect_fields.update_values(magnitude=new_value)
        else:
            new_value = 1
        return new_value


class Duration_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Duration",
                "initial_value" : '0', "effect_fields" : ''}
    required_attributes = ("effect_fields", )
    autoreferences = ("effect_fields", )

    def on_increment(self, current_value):
        if current_value == "passive":
            return current_value
        new_value = int(current_value) + 1
        self.effect_fields.update_values(duration=new_value)
        return new_value

    def on_decrement(self, current_value):
        if current_value == "passive":
            return current_value
        new_value = int(current_value) - 1
        if new_value >= 0:
            self.effect_fields.update_values(duration=new_value)
        else:
            new_value = current_value
        return new_value


class Effect_Fields(pride.gui.gui.Container):

    defaults = {"tab" : None, "ability_fields" : '', "reaction_row" : '',
                "effect" : None}
    required_attributes = ("ability_fields", )
    autoreferences = ("effect_type_selector", "influence_selector", "row2",
                      "element_selector", "magnitude_field", "duration_field",
                      "reaction_selector", "reaction_row", "trigger_selector",
                      "reaction_target_selector", "ability_fields", "tab")

    def __init__(self, **kwargs):
        super(Effect_Fields, self).__init__(**kwargs)

        if self.effect is None:
            self.effect = effect = effects.Damage.from_info(magnitude=1, element="blunt")
            self.ability_fields.ability.add_effect(effect)
        else:
            effect = self.effect
        info = effect.defaults
        # name   effect type   influence
        # element   Magnitude   duration  reaction
        # triggered     reaction targets
        row1 = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        row1.create(Name_Field, pack_mode="left", write_field_method=self._write_name,
                    orientation="stacked", initial_value=info["name"])
        _effect_type = effect.__name__
        self.effect_type_selector = row1.create(Effect_Type_Selector,
                                                initial_value=_effect_type,
                                                effect_fields=self)
        if _effect_type in ("Damage", "Heal"):
            selector_type = Influence_Selector_Permanent
        elif _effect_type in ("Buff", "Debuff"):
            selector_type = Influence_Selector_Temporary
        else:
            assert _effect_type == "Movement", _effect_type
            selector_type = Influence_Selector_Position
        self.influence_selector = row1.create(selector_type, initial_value=info["influence"].split('.')[-1],
                                              effect_fields=self)
        row2 = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        self.row2 = row2
        if _effect_type == "Damage":
            self.element_selector = row2.create(Element_Selector, initial_value=info["element"],
                                                effect_fields=self)
        self.magnitude_field = row2.create(Magnitude_Field, initial_value=info["magnitude"],
                                           effect_fields=self)
        if self.ability_fields.active_or_passive == "Passive":
            initial_value = "passive"
        else:
            initial_value = info["duration"]
        self.duration_field = row2.create(Duration_Field, initial_value=initial_value,
                                          effect_fields=self)
        self.reaction_selector = row2.create(Reaction_Selector, initial_value=info["reaction"],
                                             effect_fields=self)

    def update_values(self, **kwargs):
        self.effect.defaults.update(kwargs)
        ability = self.ability_fields
        ability.remove_effect(self.effect)
        ability.add_effect(self.effect)
        self.ability_fields.update_costs()

    def _write_name(self, field_name, value):
        self.effect.defaults["name"] = value
        self.tab.text = value
        self.pack()

    def open_reactions(self):
        if self.reaction_row:
            self.reaction_row.show()
        else:
            reaction_row = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
            self.reaction_row = reaction_row
            self.trigger_selector = reaction_row.create(Trigger_Selector,
                                                        effect_fields=self)
            self.reaction_target_selector = reaction_row.create(Reaction_Target_Selector,
                                                                effect_fields=self)

    def close_reactions(self):
        if self.reaction_row:
            self.reaction_row.hide()

    def add_effect(self, effect_type):
        self.effect.defaults["effect"] = effect_type

    def remove_effect(self, effect_type):
        if "effect" in self.effect.defaults:
            del self.effect.defaults["effect"]

    def delete(self):
        del self.effect
        super(Effect_Fields, self).delete()


class Effect_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed effect", "delete_tip" : "Delete this effect"}

    def delete_tab(self):
        window = self.window
        effect = window.effect
        ability = window.parent.ability
        ability.remove_effect(effect)
        super(Effect_Tab, self).delete_tab()


class Effect_Selection_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"tab_type" : Effect_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Effects", "window_type" : Effect_Fields,
                "ability_fields" : '', "ability" : None,
                "new_button_tip" : "Create a new effect for this ability"}
    required_attributes = ("ability_fields", )

    def __init__(self, **kwargs):
        super(Effect_Selection_Window, self).__init__(**kwargs)
        for effect_type in self.ability.effects:
            tab_kwargs = {"text" : effect_type.defaults["name"]}
            window_kwargs = {"effect" : effect_type}
            self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        try:
            window_kwargs.update({"ability_fields" : self.ability_fields})
        except AttributeError:
            if window_kwargs is not None:
                raise
            window_kwargs = {"ability_fields" : self.ability_fields}
        return super(Effect_Selection_Window, self).new_tab(window_kwargs, tab_kwargs)


class Ability_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Ability", "delete_tip" : "Delete this ability"}

    def deselect(self, next_active_object):
        super(Ability_Tab, self).deselect(next_active_object)
        window = self.window
        ability = window.ability
        character = window.character
        ability_name = ability.name
        tree = self.parent.parent.tree
        self.text = self.text.strip()
        if self.text != ability_name:
            tree.remove_ability(ability)
            ability.name = self.text
            try:
                tree.add_ability(ability)
            except ValueError:
                pass
            else:
                return
            if '(' in ability_name:
                open_paren = ability_name.rfind('(')
                close_paren = ability_name.rfind(')')
                number = int(ability_name[open_paren + 1:close_paren])
                ability_name = (ability_name[:open_paren] + ability_name[close_paren + 1:]).rstrip()
            else:
                number = 0
            while True:
                ability.name = ability_name + " ({})".format(number)
                try:
                    tree.add_ability(ability)
                except ValueError:
                    number += 1
                else:
                    break
            self.text = ability.name

    def delete_tab(self):
        window = self.window
        ability = window.ability
        tree = window.parent.tree.delete_ability(ability)
        assert ability.deleted
        #del window.ability # already happens when window is deleted
        super(Ability_Tab, self).delete_tab()


class Ability_Selection_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"tab_type" : Ability_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Abilities", "window_type" : Ability_Fields,
                "character" : '', "character_screen" : '', "tree" : '',
                "new_button_tip" : "Create a new ability in this tree"}
    required_attributes = ("character", "character_screen", "tree")

    def __init__(self, **kwargs):
        super(Ability_Selection_Window, self).__init__(**kwargs)
        tree = self.tree
        for ability_name in tree.abilities:
            tab_kwargs = {"text" : ability_name}
            window_kwargs = {"ability" : getattr(tree, ability_name),
                             "tree" : tree}
            self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        if window_kwargs is None:
            number = 0
            _kwargs = {"effects" : [effects.Damage], "target_count" : 1,
                       "range" : 0, "aoe" : 1}
            ability = abilities.Active_Ability.from_info(name="Unnamed Ability",
                                                         **_kwargs)
            while True:
                try:
                    self.tree.add_ability(ability)
                except ValueError:
                    ability.delete()
                    ability = abilities.Active_Ability.from_info(name="Unnamed Ability ({})".format(number),
                                                                **_kwargs)
                    number += 1
                else:
                    window_kwargs = {"ability" : ability, "tree" : self.tree}
                    assert tab_kwargs is None
                    tab_kwargs = {"text" : ability.name}
                    break
        else:
            assert window_kwargs["ability"].name in self.tree.abilities, (window_kwargs["ability"].name, self.tree.abilities)
        window_kwargs.update({"character" : self.character, "character_screen" : self.character_screen})
        super(Ability_Selection_Window, self).new_tab(window_kwargs, tab_kwargs)


class Ability_Tree_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "Unnamed Ability Tree", "editable" : True,
                "delete_tip" : "Delete this tree and all abilities in it"}

    def deselect(self, next_active_object):
        super(Ability_Tree_Tab, self).deselect(next_active_object)
        window = self.window
        tree = window.tree
        character = window.character
        tree_name = tree.name
        self.text = self.text.strip()
        if self.text != tree_name:
            character.abilities.remove_tree(tree)
            tree.name = self.text
            try:
                character.abilities.add_tree(tree)
            except ValueError:
                pass
            else:
                return
            if '(' in tree_name:
                open_paren = tree_name.rfind('(')
                close_paren = tree_name.rfind(')')
                number = int(tree_name[open_paren + 1:close_paren])
                tree_name = (tree_name[:open_paren] + tree_name[close_paren + 1:]).rstrip()
            else:
                number = 0
            while True:
                tree.name = tree_name + " ({})".format(number)
                try:
                    character.abilities.add_tree(tree)
                except ValueError:
                    number += 1
                else:
                    break
            self.text = tree.name

    def delete_tab(self):
        window = self.window
        window.character.abilities.delete_tree(window.tree)
        super(Ability_Tree_Tab, self).delete_tab()


class Ability_Tree_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"tab_type" : Ability_Tree_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Ability Trees", "window_type" : Ability_Selection_Window,
                "character" : '', "character_screen" : '',
                "new_button_tip" : "Create a new ability tree"}
    required_attributes = ("character", "character_screen")

    def __init__(self, **kwargs):
        super(Ability_Tree_Window, self).__init__(**kwargs)
        _abilities = self.character.abilities
        for ability_tree in _abilities.ability_trees:
            if ability_tree == "Misc":
                continue
            tab_kwargs = {"text" : ability_tree}
            window_kwargs = {"tree" : getattr(_abilities, ability_tree)}
            self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        if window_kwargs is None:
            number = 0
            tree = abilities.Ability_Tree(name="Unnamed Ability Tree")
            while True:
                try:
                    self.character.abilities.add_tree(tree)
                except ValueError:
                    tree.delete()
                    tree = abilities.Ability_Tree(name="Unnamed Ability Tree ({})".format(number))
                    number += 1
                else:
                    window_kwargs = {"tree" : tree}
                    assert tab_kwargs is None
                    tab_kwargs = {"text" : tree.name}
                    break
        else:
            assert window_kwargs["tree"].name in self.character.abilities
        window_kwargs.update({"character" : self.character, "character_screen" : self.character_screen})
        super(Ability_Tree_Window, self).new_tab(window_kwargs, tab_kwargs)


class View_Stats_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "View stats", "include_delete_button" : False}


class View_Abilities_Tab(pride.gui.widgets.tabs.Tab_Button):

    defaults = {"text" : "View abilities", "include_delete_button" : False}


class Stat_Window(pride.gui.gui.Window):

    defaults = {"pack_mode" : "main", "character_screen" : '', "character" : None}
    required_attributes = ("character_screen", "character")
    autoreferences = ("character_screen", )

    def __init__(self, **kwargs):
        super(Stat_Window, self).__init__(**kwargs)
        character_screen = self.character_screen
        self.create(Attribute_Fields, pack_mode="top",
                    target_object=self.character.attributes,
                    balance=self.character, balance_name="xp")
        self.create(Affinity_Fields, pack_mode="top",
                    target_object=self.character.affinities,
                    balancer=self.character, balance_name="xp")


class Switcher_Window(pride.gui.widgets.tabs.Tab_Switching_Window):

    _info = (("View Stats", "View attributes, affinities, and current status"),
             ("View Abilities", "View ability information and effect details"),
             ("View Options", "Modify settings and save the game"))
    _info = (pride.gui.widgets.tabs.Tab_Button.from_info(text=text, include_delete_button=False,
                                                         tip_bar_text=tip)
             for text, tip in _info)
    defaults = {"tab_types" : tuple(_info),
                "window_types" : (Stat_Window, Ability_Tree_Window, "game3.gui.options.Options_Window"),
                "character_screen" : '', "character" : ''}
    del _info

    def create_windows(self):
        stat_tab, ability_tab, options_tab = self.tab_bar.tabs
        character_screen = self.character_screen
        stat_window = self.create(self.window_types[0], tab=stat_tab,
                                  character_screen=character_screen,
                                  character=self.character)
        ability_window = self.create(self.window_types[1], tab=ability_tab,
                                     character_screen=character_screen,
                                     character=self.character)
        options_window = self.create(self.window_types[2], tab=options_tab)
        ability_window.hide()
        options_window.hide()
        stat_tab.window = stat_window
        stat_tab.indicator.enable_indicator()
        ability_tab.window = ability_window
        options_tab.window = options_window


class Status_Indicator(pride.gui.gui.Container):

    defaults = {"character" : '', "pack_mode" : "top", "h_range" : (0, 40)}
    required_attributes = ("character", )
    autoreferences = ("character", )

    def __init__(self, **kwargs):
        #print type(kwargs["character"])
        super(Status_Indicator, self).__init__(**kwargs)
        _character = self.character
        health_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        health_segment.create("pride.gui.gui.Container", text="Health",
                              pack_mode="top",
                              tip_bar_text="Health decreases as you take damage")
        self.health_indicator = health_segment.create("pride.gui.gui.Container",
                                                      text=_character.format_health_stats(),
                                                      pack_mode="top",
                                                      tip_bar_text="current/max health, + health restored, - incoming damage decreased")

        energy_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        energy_segment.create("pride.gui.gui.Container", text="Energy",
                              pack_mode="top",
                              tip_bar_text="Energy enables you to use abilities")
        self.energy_indicator = energy_segment.create("pride.gui.gui.Container",
                                                      text=_character.format_energy_stats(),
                                                      pack_mode="top",
                                                      tip_bar_text="current/max energy, + energy restored, - to energy costs")

        movement_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        movement_segment.create("pride.gui.gui.Container", pack_mode="top",
                                text="Movement",
                                tip_bar_text="Movement determines how far and how frequently you can move")
        self.movement_indicator = movement_segment.create("pride.gui.gui.Container",
                                                          pack_mode="top",
                                                          text=_character.format_movement_stats(),
                                                          tip_bar_text="current/max movement, + movement restored, - to movement costs")


class Character_Screen(pride.gui.gui.Window):

    defaults = {"stat_window" : None, "ability_window" : None, "character" : None,
                "_file_selector" : None}
    required_attributes = ("character", )
    autoreferences = ("status_indicator", "_file_selector")

    def _get_xp(self):
        return self.character.xp
    def _set_xp(self, value):
        self.character.xp = value
    xp = property(_get_xp, _set_xp)

    def __init__(self, **kwargs):
        super(Character_Screen, self).__init__(**kwargs)
        top = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        name_field = top.create(Name_Field, pack_mode="left", initial_value=self.character.name,
                                write_field_method=self._write_name)
        xp_segment = top.create("pride.gui.gui.Container", pack_mode="left", w_range=(0, 200))
        xp_segment.create("pride.gui.gui.Container", text="XP points remaining", pack_mode="top")
        self.xp_indicator = xp_segment.create("pride.gui.gui.Container", text=str(self.xp), pack_mode="top")
        _character = self.character
        self.status_indicator = self.create(Status_Indicator, character=_character)

        main_window = self.create(Switcher_Window, pack_mode="main",
                                  character_screen=self,
                                  character=_character)

    def _write_name(self, field_name, name):
        assert field_name == "Name", field_name
        self.character.name = name

    def _write_attribute(self, attribute, value):
        _character = self.character
        setattr(_character.attributes, attribute, int(value))
        status_indicator = self.status_indicator
        if attribute in ("toughness", "regeneration", "soak"):
            indicator = status_indicator.health_indicator
            indicator.text = _character.format_health_stats()
        elif attribute in ("willpower", "recovery", "grace"):
            indicator = status_indicator.energy_indicator
            indicator.text = _character.format_energy_stats()
        else:
            assert attribute in ("mobility", "recuperation", "conditioning")
            indicator = status_indicator.movement_indicator
            indicator.text = _character.format_movement_stats()

    def _write_affinity(self, affinity, value):
        setattr(self.character.affinities, affinity, int(value))

    def _modify_xp(self, adjustment):
        assert self.xp == int(self.xp_indicator.text), (self.xp, self.xp_indicator.text)
        self.xp += adjustment
        if not self.xp_indicator.deleted:
            self.xp_indicator.text = str(self.xp)

    def increment_xp(self, current_level):
        current_level = int(current_level)
        if current_level > 0:
            cost = game3.rules.calculate_acquisition_cost(current_level)
            self.xp += cost
            indicator = self.xp_indicator
            indicator.text = str(int(indicator.text) + cost)
            return current_level - 1
        else:
            return current_level

    def decrement_xp(self, current_level):
        current_level = int(current_level)
        cost = game3.rules.calculate_acquisition_cost(current_level + 1)
        if self.xp >= cost:
            self.xp -= cost
            indicator = self.xp_indicator
            indicator.text = str(int(indicator.text) - cost)
            return current_level + 1
        else:
            return current_level

    def save_character(self):
        if self.character._character_file:
            self.show_status("Saving...")
            self.character.to_sheet(self.character._character_file)
            self.character._character_file = ''
        #    self.hide_status()
        else:
            assert self._file_selector is None
            self._file_selector = self.parent.create("game3.gui.window.File_Selector",
                                                     write_field_method=self._write_character_filename,
                                                     file_category="character",
                                                     delete_callback=self.close_file_selector)
            self.hide()

    def close_file_selector(self):
        try:
            selector = self._file_selector
        except KeyError:
            pass
        else:
            assert not selector.deleted
            selector.delete_callback = None
            selector.delete()
        self._file_selector = None
        self.show()

    def _write_character_filename(self, field_name, value):
        self.parent_application.update_recent_files(value, "character")
        self.character._character_file = value
        self.close_file_selector()
        self.save_character()

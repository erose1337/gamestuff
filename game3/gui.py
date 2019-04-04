import os

import pride.gui.gui
import pride.gui.widgetlibrary
from pride.functions.utilities import slide

import character
import attributes
import affinities
import abilities
import effects
import elements
import rules


class Name_Field(pride.gui.widgetlibrary.Field):

    defaults = {"field_name" : "Name", "initial_value" : ''}


class Attribute_Fields(pride.gui.gui.Container):

    defaults = {"write_field_method" : None, "decrement_xp" : None,
                "increment_xp" : None, "character" : None}
    required_attributes = ("write_field_method", "decrement_xp", "increment_xp",
                           "character")

    def __init__(self, **kwargs):
        super(Attribute_Fields, self).__init__(**kwargs)
        self.create_attribute_fields()

    def create_attribute_fields(self):
        self._create_column("health", ("toughness", "regeneration", "soak"))
        self._create_column("energy", ("willpower", "recovery", "grace"))
        self._create_column("movement", ("mobility", "recuperation", "conditioning"))

    def _create_column(self, column_name, column_attributes):
        field_kwargs = {"on_increment" : self.decrement_xp,
                        "on_decrement" : self.increment_xp}
        _attributes = self.character.attributes
        _write_attribute = self.write_field_method
        column = self.create("pride.gui.gui.Container", pack_mode="left")
        column.create("pride.gui.gui.Container", text=column_name,
                      pack_mode="top", h_range=(0, 40))
        for attribute in column_attributes:
            def callback(value, attribute=attribute):
                _write_attribute(attribute, value)
            field_kwargs["initial_value"] = str(getattr(_attributes, attribute))
            column.create(pride.gui.widgetlibrary.Spin_Field, field_name=attribute,
                          write_field_method=callback, **field_kwargs)


class Affinity_Fields(pride.gui.gui.Container):

    defaults = {"write_field_method" : None, "decrement_xp" : None, "character" : None,
                "increment_xp" : None, "scroll_bars_enabled" : True}
    required_attributes = ("write_field_method", "decrement_xp", "increment_xp",
                           "character")

    def __init__(self, **kwargs):
        super(Affinity_Fields, self).__init__(**kwargs)
        field_kwargs = {"on_increment" : self.decrement_xp,
                        "on_decrement" : self.increment_xp,
                        "pack_mode" : "left"}
        character_affinities = self.character.affinities
        _write_affinity = self.write_field_method
        for _affinities in slide(affinities.Affinities.affinities, 3):
            row = self.create("pride.gui.gui.Container", pack_mode="top")
            for affinity in _affinities:
                def callback(value, affinity=affinity):
                    _write_affinity(affinity, value)
                field_kwargs["initial_value"] = str(getattr(character_affinities, affinity))
                row.create(pride.gui.widgetlibrary.Spin_Field, field_name=affinity,
                           write_field_method=callback, **field_kwargs)


class XP_Cost_Indicator(pride.gui.gui.Container):

    def __init__(self, **kwargs):
        super(XP_Cost_Indicator, self).__init__(**kwargs)
        self.create("pride.gui.gui.Button", text="XP cost")
        self.display = self.create("pride.gui.gui.Button", text='0').reference


class Energy_Cost_Indicator(pride.gui.gui.Container):

    defaults = {"pack_mode" : "left", "w_range" : (0, 120)}

    def __init__(self, **kwargs):
        super(Energy_Cost_Indicator, self).__init__(**kwargs)
        self.create("pride.gui.gui.Button", text="energy cost")
        self.displayer = self.create("pride.gui.gui.Button", text='0').reference


class Active_Passive_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Active or Passive:", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("Active", "Passive")),
                "pack_mode" : "left", "ability_fields" : ''}

    def on_dropdown_selection(self, selection):
        ability_fields = pride.objects[self.ability_fields]
        if selection == "Active":
            if ability_fields.active_or_passive != "Active":
                ability_fields.active_or_passive = "Active"
                for reference in pride.objects[ability_fields.effects_window].window_listing:
                    effect_fields = pride.objects[reference]
                    effect_fields.update_values(duration=0)
                    duration_field = pride.objects[effect_fields.duration_field]
                    pride.objects[duration_field.field].text = '0'
                ability_fields.update_costs()
        else:
            assert selection == "Passive"
            if ability_fields.active_or_passive != "Passive":
                ability_fields.active_or_passive = "Passive"
                ability_fields.update_values(range="self", target_count=1)

                for reference in pride.objects[ability_fields.effects_window].window_listing:
                    effect_fields = pride.objects[reference]
                    effect_fields.update_values(duration=0)
                    pride.objects[pride.objects[effect_fields.duration_field].field].text = "passive"

                pride.objects[pride.objects[ability_fields.range_field].field].text = "self"
                pride.objects[pride.objects[ability_fields.target_count_field].field].text = '1'


class Homing_Type_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Homing", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("True", "False")),
                "ability_fields" : '', "pack_mode" : "left",
                "w_range" : (0, 120)}

    def on_dropdown_selection(self, selection):
        if selection == "True":
            value = True
        else:
            value = False
        pride.objects[self.ability_fields].update_values(homing=value)


class Effect_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed Effect"}


class Range_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Range",
                "initial_value" : "self", "ability_fields" : ''}
    required_attributes = ("ability_fields", )

    def on_increment(self, current_value):
        if pride.objects[self.ability_fields].active_or_passive == "Passive":
            return "self"
        if current_value == "self":
            new_value = 0
        else:
            new_value = int(current_value) + 1
        pride.objects[self.ability_fields].update_values(range=new_value)
        return new_value

    def on_decrement(self, current_value):
        if current_value == "self":
            return "self"
        else:
            new_value = int(current_value) - 1
            changes = dict()
            ability_fields = pride.objects[self.ability_fields]
            if new_value == -1:
                new_value = "self"
                changes["target_count"] = 1
                pride.objects[pride.objects[ability_fields.target_count_field].field].text = '1'
            changes["range"] = new_value
            ability_fields.update_values(**changes)
            return new_value


class Aoe_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "AoE", "initial_value" : '1',
                "ability_fields" : ''}

    def on_increment(self, current_value):
        new_value = int(current_value) + 1
        pride.objects[self.ability_fields].update_values(aoe=new_value)
        return new_value

    def on_decrement(self, current_value):
        new_value = int(current_value) - 1
        if new_value > 0:
            pride.objects[self.ability_fields].update_values(aoe=new_value)
        else:
            new_value += 1
        return new_value


class Target_Count_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Target count",
                "initial_value" : '1', "ability_fields" : ''}

    def on_increment(self, current_value):
        ability_fields = pride.objects[self.ability_fields]
        if ability_fields.active_or_passive == "Active" and ability_fields.ability.range != "self":
            new_value = int(current_value) + 1
        else:
            new_value = 1
        ability_fields.update_values(target_count=new_value)
        return new_value

    def on_decrement(self, current_value):
        current_value = int(current_value)
        ability_fields = pride.objects[self.ability_fields]
        if ability_fields.active_or_passive == "Active":
            if current_value > 1:
                new_value = current_value - 1
                ability_fields.update_values(target_count=new_value)
                return new_value
        return current_value


class Ability_Fields(pride.gui.gui.Container):

    defaults = {"tab" : '', "character" : None, "active_or_passive" : "Active",
                "character_screen" : '', "_old_xp_cost" : 0}
    mutable_defaults = {"ability" : lambda: abilities.Active_Ability.from_info(name="Unnamed Ability",
                                                                               effects=[effects.Damage, ],
                                                                               target_count=1, range=0,
                                                                               aoe=1)()}
    required_attributes = ("character", "character_screen")

    def __init__(self, **kwargs):
        super(Ability_Fields, self).__init__(**kwargs)
        ability = self.ability
        # name, xp cost energy cost
        # active/passive, range, target count, aoe
        # effects
        row1 = self.create("pride.gui.gui.Container", h_range=(0, 40))
        row1.create(Name_Field, pack_mode="left", initial_value=ability.name,
                    write_field_method=self._write_ability_name)
        self.xp_cost_indicator = row1.create(XP_Cost_Indicator, pack_mode="left", w_range=(0, 120)).reference
        self.energy_cost_indicator = row1.create(Energy_Cost_Indicator).reference
        self.homing_selector = row1.create(Homing_Type_Selector, initial_value=ability.homing,
                                           ability_fields=self.reference).reference

        row2 = self.create("pride.gui.gui.Container", h_range=(0, 40))
        if isinstance(ability, abilities.Active_Ability):
            self.active_or_passive = "Active"
        else:
            self.active_or_passive = "Passive"
        self.active_passive_selector = row2.create(Active_Passive_Selector, initial_value=self.active_or_passive,
                                                   ability_fields=self.reference).reference
        self.range_field = row2.create(Range_Field, initial_value=ability.range,
                                       ability_fields=self.reference).reference
        self.target_count_field = row2.create(Target_Count_Field, initial_value=ability.target_count,
                                              ability_fields=self.reference).reference
        row2.create(Aoe_Field,initial_value=ability.aoe, ability_fields=self.reference)

        self.effects_window = self.create(Effect_Selection_Window, ability=ability,
                                          ability_fields=self.reference).reference
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
        if pride.objects[self.active_passive_selector].selection == "Active":
            if not isinstance(ability, abilities.Active_Ability):
                ability = abilities.Active_Ability.from_info(**kwargs)()
        else:
            if not isinstance(ability, abilities.Passive_Ability):
                ability = abilities.Passive_Ability.from_info(**kwargs)()
        self.ability = ability
        energy_cost = ability.calculate_ability_cost(self.character, None)
        pride.objects[pride.objects[self.energy_cost_indicator].displayer].text = str(energy_cost)

        character_screen = pride.objects[self.character_screen]
        xp_cost = rules.calculate_ability_acquisition_cost(self.character, ability)
        character_screen._modify_xp(self._old_xp_cost)
        character_screen._modify_xp(-xp_cost)
        self._old_xp_cost = xp_cost
        pride.objects[pride.objects[self.xp_cost_indicator].display].text = str(xp_cost)

    def _write_ability_name(self, field_name, name):
        self.ability.name = name
        pride.objects[self.tab].set_text(name)
        self.pack() # because of scale_to_text

    def delete(self):
        pride.objects[self.character_screen]._modify_xp(self._old_xp_cost)
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

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(trigger=selection)


class Effect_Type_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Effect type", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(_type)
                                      for _type in ("Damage", "Heal", "Buff", "Debuff",
                                                    "Movement")),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        effect_fields = pride.objects[self.effect_fields]
        effect = effect_fields.effect
        self.remove_old_effect(effect_fields, effect)

        info = effect.defaults
        kwargs = {"name" : info["name"], "influence" : info["influence"],
                  "magnitude" : info["magnitude"], "duration" : info["duration"]}

        self.toggle_element_selector(selection, effect_fields, kwargs)
        selector = pride.objects[effect_fields.influence_selector]

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
        ability_fields = pride.objects[effect_fields.ability_fields]
        ability_fields.add_effect(effect)
        ability_fields.update_costs()

    def remove_old_effect(self, effect_fields, effect):
        ability_fields = pride.objects[effect_fields.ability_fields]
        ability_fields.remove_effect(effect)

    def toggle_element_selector(self, selection, effect_fields, kwargs):
        if selection != "Damage":
            if effect_fields.element_selector is not None:
                pride.objects[effect_fields.element_selector].delete()
                effect_fields.element_selector = None
        else:
            if effect_fields.element_selector is None:
                row2 = pride.objects[effect_fields.row2]
                effect_fields.element_selector = row2.create(Element_Selector, effect_fields=effect_fields.reference).reference
            kwargs["element"] = pride.objects[effect_fields.element_selector].selection

    def _select_type(self, selector, effect_fields, kwargs, selector_type):
        if not isinstance(selector, selector_type):
            row = selector.parent
            selector.delete()
            selector = row.create(selector_type, effect_fields=effect_fields.reference)
            effect_fields.influence_selector = selector.reference
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

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(influence=selection)


class Influence_Selector_Temporary(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : tuple([pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(influence, "attributes.{}".format(influence))
                                       for influence in attributes.Attributes.attributes]),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(influence=selection)


class Influence_Selector_Position(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Influence", "orientation" : "stacked",
                "entry_types" : (pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info("position"), ),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(influence=selection)


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

    def on_dropdown_selection(self, selection):
        effect_fields = pride.objects[self.effect_fields]
        update_info = False
        if selection == "True":
            effect_fields.open_reactions()
            if not effect_fields.effect.defaults["reaction"]:
                update_info = True
                effect_type = pride.objects[effect_fields.effect_type_selector].selection
                new_effect = getattr(effects, effect_type).from_info(**effect_fields.effect.defaults)
        else:
            effect_fields.close_reactions()
            if effect_fields.effect.defaults["reaction"]:
                update_info = True
                effect_type = pride.objects[effect_fields.effect_type_selector].selection
                new_effect = getattr(effects, effect_type).from_info(**effect_fields.effect.defaults)
        if update_info:
            effect_fields.remove_effect(effect_fields.effect)
            ability_fields = pride.objects[effect_fields.ability_fields]
            ability_fields.ability.remove_effect(effect_fields.effect)
            effect_fields.effect = new_effect
            ability_fields.ability.add_effect(new_effect)


class Reaction_Target_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Reaction target", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(target)
                                      for target in ("reacting actor", "triggering actor")),
                "pack_mode" : "left"}

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(target=selection)


class Element_Selector(pride.gui.widgetlibrary.Dropdown_Field):

    defaults = {"field_name" : "Element", "orientation" : "stacked",
                "entry_types" : tuple(pride.gui.widgetlibrary.Dropdown_Box_Entry.from_info(element)
                                      for element in elements.ELEMENTS),
                "effect_fields" : '', "pack_mode" : "left"}
    required_attributes = ("effect_fields", )

    def on_dropdown_selection(self, selection):
        pride.objects[self.effect_fields].update_values(element=selection)


class Magnitude_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Magnitude",
                "initial_value" : '1', "effect_fields" : ''}
    required_attributes = ("effect_fields", )

    def on_increment(self, current_value):
        new_value = int(current_value) + 1
        pride.objects[self.effect_fields].update_values(magnitude=new_value)
        return new_value

    def on_decrement(self, current_value):
        new_value = int(current_value) - 1
        if new_value > 0:
            pride.objects[self.effect_fields].update_values(magnitude=new_value)
        else:
            new_value = 1
        return new_value


class Duration_Field(pride.gui.widgetlibrary.Spin_Field):

    defaults = {"pack_mode" : "left", "field_name" : "Duration",
                "initial_value" : '0', "effect_fields" : ''}
    required_attributes = ("effect_fields", )

    def on_increment(self, current_value):
        if current_value == "passive":
            return current_value
        new_value = int(current_value) + 1
        pride.objects[self.effect_fields].update_values(duration=new_value)
        return new_value

    def on_decrement(self, current_value):
        if current_value == "passive":
            return current_value
        new_value = int(current_value) - 1
        if new_value >= 0:
            pride.objects[self.effect_fields].update_values(duration=new_value)
        else:
            new_value = current_value
        return new_value


class Effect_Fields(pride.gui.gui.Container):

    defaults = {"tab" : None, "ability_fields" : '', "reaction_row" : '',
                "effect" : None}
    required_attributes = ("ability_fields", )

    def __init__(self, **kwargs):
        super(Effect_Fields, self).__init__(**kwargs)

        if self.effect is None:
            self.effect = effect = effects.Damage.from_info(magnitude=1)
            pride.objects[self.ability_fields].ability.add_effect(effect)
        else:
            effect = self.effect
        info = effect.defaults
        # name   effect type   influence
        # element   Magnitude   duration
        row1 = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        row1.create(Name_Field, pack_mode="left", write_field_method=self._write_name,
                    orientation="stacked", initial_value=info["name"])
        _effect_type = effect.__name__
        self.effect_type_selector = row1.create(Effect_Type_Selector,
                                                initial_value=_effect_type,
                                                effect_fields=self.reference).reference
        if _effect_type in ("Damage", "Heal"):
            selector_type = Influence_Selector_Permanent
        elif _effect_type in ("Buff", "Debuff"):
            selector_type = Influence_Selector_Temporary
        else:
            assert _effect_type == "Movement", _effect_type
            selector_type = Influence_Selector_Position
        self.influence_selector = row1.create(selector_type, initial_value=info["influence"].split('.')[-1],
                                              effect_fields=self.reference).reference
        row2 = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        self.row2 = row2.reference
        if _effect_type == "Damage":
            self.element_selector = row2.create(Element_Selector, initial_value=info["element"],
                                                effect_fields=self.reference).reference
        self.magnitude_field = row2.create(Magnitude_Field, initial_value=info["magnitude"],
                                           effect_fields=self.reference).reference
        if pride.objects[self.ability_fields].active_or_passive == "Passive":
            initial_value = "passive"
        else:
            initial_value = info["duration"]
        self.duration_field = row2.create(Duration_Field, initial_value=initial_value,
                                          effect_fields=self.reference).reference
        self.reaction_selector = row2.create(Reaction_Selector, initial_value=info["reaction"],
                                             effect_fields=self.reference)
        
    def update_values(self, **kwargs):
        self.effect.defaults.update(kwargs)
        ability = pride.objects[self.ability_fields]
        ability.remove_effect(self.effect)
        ability.add_effect(self.effect)
        pride.objects[self.ability_fields].update_costs()

    def _write_name(self, field_name, value):
        self.effect.name = value
        pride.objects[self.tab].set_text(value)
        self.pack()

    def open_reactions(self):
        if self.reaction_row:
            pride.objects[self.reaction_row].show()
        else:
            reaction_row = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
            self.reaction_row = reaction_row.reference
            reaction_row.create(Trigger_Selector, effect_fields=self.reference)
            reaction_row.create(Reaction_Target_Selector, effect_fields=self.reference)

    def close_reactions(self):
        if self.reaction_row:
            pride.objects[self.reaction_row].hide()

    def add_effect(self, effect_type):
        self.effect.defaults["effect"] = effect_type

    def remove_effect(self, effect_type):
        if "effect" in self.effect.defaults:
            del self.effect.defaults["effect"]


class Effect_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed effect"}


class Effect_Selection_Window(pride.gui.widgetlibrary.Tabbed_Window):

    defaults = {"tab_type" : Effect_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Effects", "window_type" : Effect_Fields,
                "ability_fields" : '', "ability" : None}
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
            if window_args is not None:
                raise
            window_kwargs = {"ability_fields" : self.ability_fields}
        super(Effect_Selection_Window, self).new_tab(window_kwargs, tab_kwargs)


class Ability_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed Ability"}


class Ability_Selection_Window(pride.gui.widgetlibrary.Tabbed_Window):

    defaults = {"tab_type" : Ability_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Abilities", "window_type" : Ability_Fields,
                "character" : '', "character_screen" : '', "tree_name" : ''}
    required_attributes = ("character", "character_screen")

    def __init__(self, **kwargs):
        super(Ability_Selection_Window, self).__init__(**kwargs)
        if self.tree_name:
            _abilities = self.character.abilities
            tree = getattr(_abilities, self.tree_name)
            for ability_name in tree.abilities:
                tab_kwargs = {"text" : ability_name}
                window_kwargs = {"ability" : getattr(tree, ability_name)}
                self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        try:
            window_kwargs.update({"character" : self.character, "character_screen" : self.character_screen})
        except AttributeError:
            if window_kwargs is not None:
                raise
            window_kwargs = {"character" : self.character, "character_screen" : self.character_screen}
        super(Ability_Selection_Window, self).new_tab(window_kwargs, tab_kwargs)


class Ability_Tree_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "Unnamed Ability Tree", "editable" : True}


class Ability_Tree_Window(pride.gui.widgetlibrary.Tabbed_Window):

    defaults = {"tab_type" : Ability_Tree_Tab, "pack_mode" : "main",
                "tab_bar_label" : "Ability Trees", "window_type" : Ability_Selection_Window,
                "character" : '', "character_screen" : ''}
    required_attributes = ("character", "character_screen")

    def __init__(self, **kwargs):
        super(Ability_Tree_Window, self).__init__(**kwargs)
        for ability_tree in self.character.abilities.ability_trees:
            if ability_tree == "Misc":
                continue
            tab_kwargs = {"text" : ability_tree}
            window_kwargs = {"tree_name" : ability_tree}
            self.new_tab(window_kwargs, tab_kwargs)

    def new_tab(self, window_kwargs=None, tab_kwargs=None):
        try:
            window_kwargs.update({"character" : self.character, "character_screen" : self.character_screen})
        except AttributeError:
            if window_kwargs is not None:
                raise
            window_kwargs = {"character" : self.character, "character_screen" : self.character_screen}
        super(Ability_Tree_Window, self).new_tab(window_kwargs, tab_kwargs)


class View_Stats_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "View stats", "include_delete_button" : False}


class View_Abilities_Tab(pride.gui.widgetlibrary.Tab_Button):

    defaults = {"text" : "View abilities", "include_delete_button" : False}


class Stat_Window(pride.gui.gui.Window):

    defaults = {"pack_mode" : "main", "character_screen" : '', "character" : None}
    required_attributes = ("character_screen", "character")

    def __init__(self, **kwargs):
        super(Stat_Window, self).__init__(**kwargs)
        character_screen = pride.objects[self.character_screen]
        self.create("pride.gui.gui.Container", text="Attributes",
                    pack_mode="top", h_range=(0, 40))
        self.create(Attribute_Fields, pack_mode="top",
                    decrement_xp=character_screen.decrement_xp,
                    increment_xp=character_screen.increment_xp,
                    write_field_method=character_screen._write_attribute,
                    character=self.character)
        self.create("pride.gui.gui.Container", text="Affinities",
                    pack_mode="top", h_range=(0, 40))
        self.create(Affinity_Fields, pack_mode="top",
                    increment_xp=character_screen.increment_xp,
                    decrement_xp=character_screen.decrement_xp,
                    write_field_method=character_screen._write_affinity,
                    character=self.character)


class Switcher_Window(pride.gui.widgetlibrary.Tab_Switching_Window):

    defaults = {"tab_types" : (View_Stats_Tab, View_Abilities_Tab),
                "window_types" : (Stat_Window, Ability_Tree_Window),
                "character_screen" : '', "character" : ''}

    def create_windows(self):
        stat_tab, ability_tab = self.tab_bar.tabs
        character_screen = self.character_screen
        stat_window = self.create(self.window_types[0], tab=stat_tab,
                                  character_screen=character_screen,
                                  character=self.character)
        ability_window = self.create(self.window_types[1], tab=ability_tab,
                                     character_screen=character_screen,
                                     character=self.character)
        ability_window.hide()
        pride.objects[stat_tab].window = stat_window.reference
        pride.objects[ability_tab].window = ability_window.reference


class Status_Indicator(pride.gui.gui.Container):

    defaults = {"character" : '', "pack_mode" : "top", "h_range" : (0, 40)}
    required_attributes = ("character", )

    def __init__(self, **kwargs):
        super(Status_Indicator, self).__init__(**kwargs)
        _character = pride.objects[self.character]
        health_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        health_segment.create("pride.gui.gui.Container", text="Health", pack_mode="top")
        self.health_indicator = health_segment.create("pride.gui.gui.Container",
                                                      text=_character.format_health_stats(),
                                                      pack_mode="top")

        energy_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        energy_segment.create("pride.gui.gui.Container", text="Energy", pack_mode="top")
        self.energy_indicator = energy_segment.create("pride.gui.gui.Container",
                                                      text=_character.format_energy_stats(),
                                                      pack_mode="top")

        movement_segment = self.create("pride.gui.gui.Container", pack_mode="left")
        movement_segment.create("pride.gui.gui.Container", pack_mode="top", text="Movement")
        self.movement_indicator = movement_segment.create("pride.gui.gui.Container",
                                                          pack_mode="top",
                                                          text=_character.format_movement_stats())


class Character_Screen(pride.gui.gui.Window):

    defaults = {"stat_window" : None, "ability_window" : None, "character" : None}
    required_attributes = ("character", "xp")

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
        self.status_indicator = self.create(Status_Indicator,
                                            character=_character.reference).reference

        main_window = self.create(Switcher_Window, pack_mode="main",
                                  character_screen=self.reference,
                                  character=_character)

    def _write_name(self, field_name, name):
        assert field_name == "Name", field_name
        self.character.name = name

    def _write_attribute(self, attribute, value):
        _character = self.character
        setattr(_character.attributes, attribute, int(value))
        status_indicator = pride.objects[self.status_indicator]
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
        self.xp_indicator.text = str(self.xp)

    def increment_xp(self, current_level):
        current_level = int(current_level)
        if current_level > 0:
            cost = rules.calculate_acquisition_cost(current_level)
            self.xp += cost
            indicator = self.xp_indicator
            indicator.text = str(int(indicator.text) + cost)
            return current_level - 1
        else:
            return current_level

    def decrement_xp(self, current_level):
        current_level = int(current_level)
        cost = rules.calculate_acquisition_cost(current_level + 1)
        if self.xp >= cost:
            self.xp -= cost
            indicator = self.xp_indicator
            indicator.text = str(int(indicator.text) - cost)
            return current_level + 1
        else:
            return current_level


class Character_File_Selector(pride.gui.widgetlibrary.Field):

    defaults = {"field_name" : "filename", "initial_value" : ''}


class Game_Window(pride.gui.gui.Application):

    defaults = {"character_creation_screen_type" : Character_Screen,
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
        self.application_window.create(self.character_creation_screen_type,
                                       character=character.Character(attributes=attributes.Attributes(),
                                                                     affinities=affinities.Affinities(),
                                                                     abilities=abilities.Abilities()))

    def load_character_screen(self):
        for item in self._splash_screen_items:
            item.delete()
        self.file_selector = self.application_window.create(Character_File_Selector,
                                                            write_field_method=self._load_character).reference

    def _load_character(self, field_name, value):
        if os.path.exists(value):
            pride.objects[self.file_selector].delete()
            _character = character.Character.from_sheet(value)
            self.application_window.create(self.character_creation_screen_type,
                                           character=_character)

    def delete(self):
        super(Game_Window, self).delete()
        raise SystemExit()

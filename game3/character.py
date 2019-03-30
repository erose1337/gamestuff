import pride.components.base
from pride.components.shell import get_selection

import actions
import parsing
import effects
import rules
import attributes
import affinities
import effects
import elements
import abilities

def get_input(prompt):
    output = ''
    while not output:
        output = raw_input(prompt)
    return output

def format_effect_queue(effect_queue):
    applied_effects = []
    counts = [] # uses two lists instead of dict to preserve order
    for effect in effect_queue[0] + effect_queue[1] + effect_queue[2]:
        effect = effect[0].name
        if effect in applied_effects:
            counts[applied_effects.index(effect)] += 1
        else:
            applied_effects.append(effect)
            counts.append(1)
            assert len(applied_effects) == len(counts)
    effect_strs = []
    for effect, count in zip(applied_effects, counts):
        effect_str = effect
        if count > 1:
            effect_str += " ({})".format(count)
        effect_strs.append(effect_str)
    return "\nEffects: {}".format(', '.join(effect_strs))

def guided_attribute_selection(creation_info):
    while True:
        attribute_points = creation_info["attribute_points_count"]()
        _attributes = attributes.Attributes()
        attribute_list = _attributes.attributes
        print("\nAttribute explanation\n" + ('-' * 79))
        print(_attributes.format_descriptions())
        print('-' * 79)
        while attribute_points:
            print(_attributes.format_attributes())
            print("Remaining points: {}".format(attribute_points))
            selection = get_selection("Select an attribute to increase: ",
                                      attribute_list)
            setattr(_attributes, selection, getattr(_attributes, selection) + 1)
            attribute_points -= 1
        print('-' * 79)
        print(_attributes.format_attributes())
        affirmative = get_selection("Keep these attributes?: ", bool)
        if affirmative:
            return _attributes

def guided_affinity_selection(creation_info):
    while True:
        affinity_points = creation_info["affinity_points_count"]()
        _affinities = affinities.Affinities()
        affinity_list = _affinities.affinities
        print("\nAffinities explanation\n" + ('-' * 79))
        print(_affinities.description)
        print('-' * 79)
        while affinity_points:
            print(_affinities.format_affinities())
            print("Remaining points: {}".format(affinity_points))
            selection = get_selection("Select an affinity to increase: ",
                                      affinity_list)
            setattr(_affinities, selection, getattr(_affinities, selection) + 1)
            affinity_points -= 1
        print('-' * 79)
        print(_affinities.format_affinities())
        affirmative = get_selection("Keep these affinities?: ", bool)
        if affirmative:
            return _affinities

def guided_ability_creation(creation_info):
    _abilities = abilities.Abilities()
    ability_count = creation_info["active_ability_points_count"]()
    potency_limit = creation_info["ability_potency_limit"]()
    effect_types = effects.EFFECT_TYPES
    element_types = elements.ELEMENTS
    stat_influences = ("health", "energy", "movement")
    attribute_influences = attributes.Attributes.attributes
    print(_abilities.description)
    print('-' * 79)
    print("Create {} active abilities".format(ability_count))
    print('-' * 79)
    _abilities = dict()
    for count in range(1):
        name = get_input("Ability name: ")
        while True:
            print("Effect types: {}".format(', '.join(effect_types)))
            effect_type = get_selection("Select an effect type: ", effect_types)
            if effect_type == "damage":
                print("Element types: {}".format(', '.join(element_types)))
                element = get_selection("Select an element: ", element_types)
            else:
                element = "null"
            if effect_type in ("damage", "heal"):
                print("Influence types: {}".format(', '.join(stat_influences)))
                influence = get_selection("Select an influence: ", stat_influences)
            elif effect_type in ("buff", "debuff"):
                print("Influence types: {}".format(', '.join(attribute_influences)))
                influence = get_selection("Select an influence", attribute_influences)
            while True:
                try:
                    _range = int(get_input("Range: "))
                    target_count = int(get_input("Target count: "))
                    aoe = int(get_input("Aoe: "))
                    magnitude = int(get_input("Magnitude: "))
                    duration = int(get_input("Duration: "))
                except ValueError:
                    continue
                else:
                    break
            break
        info = {"name" : name, "range" : _range, "target_count" : target_count,
                "aoe" : aoe, "effects" : {effect_type.title(): {"element" : element, "influence" : influence,
                                                                "magnitude" : magnitude, "duration" : duration}}}
        _abilities[name] = parsing.parse_ability(name, info)
    return abilities.Abilities.from_info({"basic" : abilities.Ability_Tree.from_info("Basic", _abilities)})

class Character(pride.components.base.Base):

    defaults = {"name" : '', "is_npc" : True, "position" : (0, 0),
                "attributes" : None, "affinities" : None, "abilities" : None}
    predefaults = {"_health" : 0, "_energy" : 0, "_health_scalar" : 10,
                   "_energy_scalar" : 10, "_base_health" : 10,
                   "_base_energy" : 10, "_movement" : 0, "_base_movement" : 1,
                   "_movement_scalar" : 1}
    mutable_defaults = {"effect_queue" : effects.NEW_EFFECT_QUEUE,
                        "reaction_effects" : list}
    required_attributes = ("attributes", "affinities", "abilities")
    post_initializer = "initialize"

    def _get_health(self):
        return self._health
    def _set_health(self, value):
        self._health = min(value, self.max_health)
    health = property(_get_health, _set_health)

    def _get_max_health(self):
        return rules.calculate_max_health(self.attributes.toughness)
    max_health = property(_get_max_health)

    def _get_energy(self):
        return self._energy
    def _set_energy(self, value):
        self._energy = max(0, min(value, self.max_energy))
    energy = property(_get_energy, _set_energy)

    def _get_max_energy(self):
        return rules.calculate_max_energy(self.attributes.willpower)
    max_energy = property(_get_max_energy)

    def _get_is_dead(self):
        return self.health <= 0
    is_dead = property(_get_is_dead)

    def _get_movement(self):
        return self._movement
    def _set_movement(self, value):
        self._movement = max(0, min(value, self.max_movement))
    movement = property(_get_movement, _set_movement)

    def _get_max_movement(self):
        return rules.calculate_max_movement(self.attributes.mobility)
    max_movement = property(_get_max_movement)

    def initialize(self):
        self.health = self.max_health
        self.energy = self.max_energy
        self.movement = self.max_movement
        self.activate_passives()

    def activate_passives(self):
        for ability in self.abilities.passive_abilities():
            ability.activate(self, self)

    def select_action(self, characters):
        if not self.is_npc:
            return actions.present_action_menu(self, characters)
        else:
            raise NotImplementedError("AI not implemented")

    def format_stats(self):
        attributes = self.attributes
        output = "{} stats\n".format(self.name) + ('-' * 79)
        line = "\n{}: {}/{}{:>26}: {}/{}{:>26}: {}/{}"
        output += line.format("health", self.health, self.max_health,
                              "energy", self.energy, self.max_energy,
                              "movement", self.movement, self.max_movement)
        output += attributes.format_attributes()
        output += format_effect_queue(self.effect_queue)
        return output

    def format_abilities(self):
        abilities = self.abilities
        output = "{}'s abilities\n".format(self.name) + ('-' * 79) + '\n'
        for ability_tree_name in abilities:
            ability_tree = getattr(abilities, ability_tree_name)
            output += "{} abilities:\n".format(ability_tree_name.title())
            for index1, chunk in enumerate(pride.functions.utilities.slide(tuple(ability_tree), 4)):
                spacing = 80 / len(chunk)
                for ability_name in chunk:
                    ability = getattr(ability_tree, ability_name)
                    _entry = " {}".format(ability_name)
                    if ability_name != "move":
                        _entry += " (cost: {})".format(ability.calculate_ability_cost(self, None))
                    _entry = _entry.ljust(spacing)
                    output += _entry
                output += '\n'
            output += '\n'
        return output

    @classmethod
    def guided_character_creation(cls):
        print("Character creation")
        name = get_input("Enter name: ")
        creation_info = rules.RULES["character creation"]
        #_attributes = guided_attribute_selection(creation_info)
        #_affinities = guided_affinity_selection(creation_info)
        _abilities = guided_ability_creation(creation_info)

    @classmethod
    def from_sheet(cls, sheet_filename):
        info = parsing.parse_character(sheet_filename)
        return cls(is_npc=False, **info)

    def to_sheet(self, sheet_filename):
        category_indicator = ('=' * 79) + "\n\n"
        entry_indicator = ('-' * 79) + '\n'
        with open(sheet_filename, 'w') as _file:
            _file.write("Character Info\n")
            _file.write(category_indicator)
            _file.write("Basic Info\n")
            _file.write(entry_indicator)
            _file.write("- name: {}\n\n".format(self.name))
            _file.write("Attributes\n")
            _file.write(entry_indicator)
            _file.write('\n'.join("- {}: {}".format(attribute, value) for attribute, value in
                                                    sorted(self.attributes.items())))
            _file.write("\n\n")
            _file.write("Resists\n")
            _file.write(entry_indicator)
            _file.write('\n'.join("- {}: {}".format(element, value) for element, value in
                                                    sorted(self.resists.items())))
            _file.write("\n\n")
            _file.write("Abilities\n")
            _file.write(category_indicator)
            for category, entries in self.abilities.items():
                _file.write("    {}\n".format(category))
                _file.write("    {}".format(category_indicator[4:]))
                for entry, fields in entries.items():
                    _file.write("    {}\n".format(entry))
                    _file.write("    {}".format(entry_indicator[4:]))
                    for field, value in sorted(fields.items()):
                        if field[:6] == "effect":
                            _file.write("    - {}:\n".format(field))
                            for _entry, _fields in value.items():
                                _file.write("        {}\n".format(_entry))
                                _file.write("        {}".format(entry_indicator[8:]))
                                for _field, _value in _fields.items():
                                    _file.write("        - {}: {}\n".format(_field, _value))
                                #_file.write('\n')
                            _file.write('\n')
                        else:
                            _file.write("    - {}: {}\n".format(field, value))
                    _file.write('\n')

    def format_health_stats(self):
        attributes = self.attributes
        regen_value = rules.calculate_attribute_value("regeneration", attributes.regeneration)
        soak_value = rules.calculate_attribute_value("soak", attributes.soak)
        return "{}/{}, +{}, -{}".format(self.health, self.max_health,
                                        regen_value, soak_value)

    def format_energy_stats(self):
        attributes = self.attributes
        recovery_value = rules.calculate_attribute_value("recovery", attributes.recovery)
        grace_value = rules.calculate_attribute_value("grace", attributes.grace)
        return "{}/{}, +{}, -{}".format(self.energy, self.max_energy,
                                        recovery_value, grace_value)

    def format_movement_stats(self):
        attributes = self.attributes
        recup_value = rules.calculate_attribute_value("recuperation", attributes.recuperation)
        conditioning_value = rules.calculate_attribute_value("conditioning", attributes.conditioning)
        return "{}/{}, +{}, -{}".format(self.movement, self.max_movement,
                                        recup_value, conditioning_value)

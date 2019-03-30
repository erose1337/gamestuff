from math import sqrt

import pride.components.base
import pride.components.shell
get_selection = pride.components.shell.get_selection

import abilities
import ai
import rules

def present_action_menu(acting_character, characters):
    ability_set = acting_character.abilities.active_abilities()
    if not ability_set:
        raise ValueError("active character has no usable abilities")

    options = ("ability sheet", "status", "use ability")
    while True:
        print("Options: {}".format(', '.join(options)))
        selection = get_selection("({}) Select an option: ".format(acting_character.name), options)
        if selection == "ability sheet":
            print(acting_character.format_abilities())
        elif selection == "status":
            for character in characters:
                print character.format_stats()
                print
        elif selection == "use ability":
            return use_ability(acting_character, characters, ability_set)

def use_ability(acting_character, characters, ability_set):
    usable_abilities = []
    for name, value in sorted(ability_set.items()):
        if isinstance(value, abilities.Move) and acting_character.movement:
            usable_abilities.append(name)
        else:
            cost = value.calculate_ability_cost(acting_character, None)
            if cost <= getattr(acting_character, value.energy_source):
                usable_abilities.append("{} (cost: {})".format(name, cost))

    #usable_abilities = [name for (name, value) in sorted(ability_set.items()) if
    #                    ai.determine_usable(acting_character, value)]
    if not usable_abilities:
        print("No usable abilities!")
        return No_Action()

    priority = 1
    while True:
        print("Usable abilities:\n- {}".format('\n- '.join(usable_abilities)))
        ability_name = get_selection("Select a ability to use: ", ability_set.keys())
        ability = ability_set[ability_name]
        if ability.range == "self":
            targets = (acting_character, )
        elif ability.range == "move":
            max_distance = acting_character.movement
            if not max_distance:
                print("No movement points left!")
                continue
            while True:
                position = raw_input("Select target position (in x, y coordinates): ")
                x, y = position.split(',', 1)
                try:
                    x = int(x.strip())
                except ValueError:
                    print("Invalid x coordinate")
                else:
                    try:
                        y = int(y.strip())
                    except ValueError:
                        print("Invalid y coordinate")
                    else:
                        targets = ((x, y), )
                        if rules.distance_between(acting_character.position, targets[0]) > acting_character.movement:
                            print("Cannot move that far; Movement points: {}".format(acting_character.movement))
                        else:
                            priority = 0
                            break
            break
        else:
            max_distance = rules.determine_range(ability.range)
            position = acting_character.position
            available_targets = []
            for character in characters:
                if rules.distance_between(position, character.position) <= max_distance:
                    available_targets.append(character)
            if not available_targets:
                print("No targets within {} for {}".format(max_distance, ability))
                continue
            else:
                target_names = []
                for count, character in enumerate(available_targets):
                    display = "{}: {}".format(count, character.name)
                    if character is acting_character:
                        display += " (self)"
                    target_names.append(display)

                targets = []
                target_count = ability.target_count
                while len(targets) != target_count:
                    print("Available targets:\n    {}".format('\n    '.join(target_names)))
                    try:
                        target_number = int(raw_input("Select target number {}/{}: ".format(len(targets) + 1, target_count)))
                    except ValueError:
                        continue
                    else:
                        targets.append(available_targets[target_number])

                if ability.aoe > 1:
                    _targets = []
                    for target in targets:
                        _targets += [character for character in characters if
                                     character != target and
                                     rules.distance_between(target.position,
                                                            character.position) <= ability.aoe]
                    targets += _targets
        break
    return Action(source=acting_character, targets=targets, ability=ability,
                  priority=priority)


class Action(pride.components.base.Base):

    defaults = {"source" : None, "targets" : tuple(), "ability" : None,
                "priority" : 1}
    required_attributes = ("source", "targets", "ability")

    def evaluate(self):
        self.ability.activate(self.source, self.targets)


class No_Action(object):

    def evaluate(self):
        return

import parsing

RULES = dict() # populated via parsing.parse_rules in main

def set_rules(rules_filename="rules.cef"):
    RULES.clear()
    RULES.update(parsing.parse_rules(rules_filename))

def calculate_ability_cost(character, ability):
    if ability.no_cost:
        return 0
    abilities_cost = RULES["abilities"]
    effect_cost_f = abilities_cost["effects_energy_cost"]
    affinity_f = RULES["attributes"]["affinity_resistance"]
    effect_cost = sum(effect_cost_f(magnitude=effect.magnitude,
                                    influence=abilities_cost["influence_{}_cost".format(effect.influence.replace("attributes.", ''))](level=0),
                                    duration=effect.duration,
                                    affinity_discount=affinity_f(level=0 if effect.element == "null" else
                                                                       getattr(character.affinities, effect.element)))
                      for effect in ability._effects)

    range = ability.range if isinstance(ability.range, int) else 1
    grace_value = RULES["attributes"]["grace_value"](level=character.attributes.grace)
    homing_cost = RULES["abilities"]["homing_cost"](value=int(ability.homing))
    return abilities_cost["abilities_energy_cost"](range=range, aoe=ability.aoe,
                                                   target_count=ability.target_count,
                                                   effect_cost=effect_cost,
                                                   grace=grace_value,
                                                   homing_cost=homing_cost)

def calculate_effect_potency(effect):
    return RULES["effects"]["{}_potency".format(effect)]

def determine_range(range):
    return RULES["abilities"]["range_value"](level=range)

def calculate_max_health(toughness):
    return RULES["attributes"]["toughness_value"](level=toughness)

def calculate_max_energy(willpower):
    return RULES["attributes"]["willpower_value"](level=willpower)

def calculate_max_movement(mobility):
    return RULES["attributes"]["mobility_value"](level=mobility)

def calculate_attribute_value(attribute, level):
    return RULES["attributes"]["{}_value".format(attribute)](level=level)

def distance_between(position1, position2):
    return RULES["misc"]["distance_calculation_result"](x1=position1[0], x2=position2[0],
                                                        y1=position1[1], y2=position2[1])

def calculate_move_cost(actor, position):
    attributes = actor.attributes
    distance = distance_between(actor.position, position)

    return RULES["misc"]["movement_cost_result"](distance=distance_between(actor.position, position),
                                                 conditioning=attributes.conditioning)

def calculate_acquisition_cost(new_level):
    return RULES["character creation"]["acquisition_cost"](level=new_level)

def calculate_ability_acquisition_cost(character, ability):
    abilities_cost = RULES["abilities"]
    effect_cost_f = abilities_cost["effects_acquire_cost"]
    affinity_f = RULES["attributes"]["affinity_resistance"]
    effect_cost = sum(effect_cost_f(magnitude=effect.magnitude,
                                    influence=abilities_cost["influence_{}_cost".format(effect.influence.replace("attributes.", ''))](level=0),
                                    duration=effect.duration,
                                    affinity_discount=affinity_f(level=0 if effect.element == "null" else
                                                                       getattr(character.affinities, effect.element)))
                      for effect in ability._effects)

    range = ability.range if isinstance(ability.range, int) else 1
    homing_cost = RULES["abilities"]["homing_cost"](value=int(ability.homing))
    return abilities_cost["abilities_acquire_cost"](range=range, aoe=ability.aoe,
                                                    target_count=ability.target_count,
                                                    effect_cost=effect_cost,
                                                    homing_cost=homing_cost)

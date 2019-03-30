# ai profiles

# "high health" : health > opponent max hit
# "low health" : health < opponent max hit
# "high energy" : energy > cost of desired ability
# "low energy" : energy < cost of desired ability
# "high movement" : movement > opponent movement + attack range
# "low movement" : movement < opponent movement + attack range

# if high health
#       if high energy:
#           if applicable buffs/debuffs are not applied yet:
#               use buffs/debuffs
#           else:
#               attack
#       else:
#            rest/recover
# else:
#       if high movement and opponent is not ranged attacker:
#           move away from opponent
#       else if high energy:
#           if opponent has low health and low energy:
#               attack
#           else if healing abilities are present:
#               use them
#           else if misc.heal provides more health than estimated damage for next turn:
#               use misc.heal
#      else:
#           heal/regenerate

import abilities
import rules

def determine_action(actor, opponent):
    high_health = determine_health(actor, opponent)
    if high_health:
        buffs = determine_applicable_buffs(actor, opponent)
        debuffs = determine_applicable_debuffs(actor, opponent)
        attacks = determine_attacks(actor, opponent)
        options = buffs + debuffs + attacks
        if options:
            return sorted(options)[-1][1]
        else:
            return "rest"
    else:
        if determine_can_dodge(actor, opponent):
            return "move"
        max_hit = determine_max_hit(opponent, actor)
        defend_health = max(actor.health - max_hit - actor.skills.defense.defend, 0)
        heal_health = max((actor.health + actor.skills.misc.heal) - max_hit, 0)
        if not defend_health or heal_health:
            return sorted(determine_attacks(actor, opponent))[-1][1]
        elif defend_health > heal_health:
            return "defend"
        else:
            return "heal"

def determine_health(actor1, actor2):
    health = actor1.health
    max_hit = determine_max_hit(actor2, actor1)
    return health > max_hit

def determine_applicable_buffs(actor1, actor2):
    return [] # abilities not implemented yet, no buffs exist

def determine_applicable_debuffs(actor1, actor2):
    return [] # abililities not implemented yet, no debuffs exist

def determine_attacks(actor1, actor2):
    offense = actor1.skills.offense
    resists = actor2.skills.resists
    soak = actor2.skills.defense.soak
    outputs = []
    for skill_name in offense:
        skill = getattr(offense, skill_name)
        if determine_usable(skill):
            element = skill.element
            resistance = getattr(resists, element).level
            damage = max(skill.level - resistance - soak, 0)
            outputs.append((damage, skill_name))
    return outputs

def determine_max_hit(actor1, actor2):
    attacks = determine_attacks(actor1, actor2)
    try:
        return sorted(attacks)[-1][0]
    except IndexError:
        return 0

def determine_ranged_attacker(actor):
    # to do: incorporate abilities into decision
    return bool(actor.skills.offense.ranged.level)

def determine_can_dodge(actor1, actor2):
    range = determine_attack_range(actor2)
    if not range:
        return True
    max_distance = determine_movement_distance(actor1)
    return max_distance > range

def determine_movement_distance(actor):
    movement = actor.skills.movement
    max_distance = movement.physical.level
    for skill_name in movement:
        distance = getattr(movement, skill_name).level
        if distance > max_distance:
            max_distance = distance
    return max_distance

def determine_attack_range(actor):
    # to do: incorporate abilities
    #        adjust calculation of max range for ranged attack?
    offense = actor.skills.offense
    ranged_attack = offense.ranged_attack
    if determine_usable(actor, ranged_attack):
        return ranged_attack.level
    else:
        if (determine_usable(offense.hand_to_hand) or
            determine_usable(offense.melee_weapon)):
            return 1
    return 0

def determine_usable(actor, action):
    if isinstance(action, abilities.Move):
        return bool(actor.movement)
    return (isinstance(action, abilities.Active_Ability) and
            action.calculate_ability_cost(actor, None) <= getattr(actor, action.energy_source))

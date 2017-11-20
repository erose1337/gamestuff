import random

ELEMENT_BONUS = {"Fire" : "Air", "Air" : "Stone", "Stone" : "Electric", 
                 "Electric" : "Water", "Water" : "Fire", "Excellence" : "None", "Neutral" : "None"}
ELEMENT_PENALTY = dict((value, key) for key, value in ELEMENT_BONUS.items())
del ELEMENT_PENALTY["None"]
ELEMENT_PENALTY["Excellence"] = "None"
ELEMENT_PENALTY["Neutral"] = "None"

    
def process_skill(party1, level, skill, toggle_name, focus1, focus2,
                  activation_chance, base_damage, alert_string):
    bonus = 0
    if toggle_name in party1.toggle_abilities:
        chance_modifier = 15
        damage_modifier = 0
    else:
        chance_modifier = damage_modifier = 0
    if random.randint(0, 100) <= activation_chance + chance_modifier:
        if skill in (focus1, focus2):
            level_modifier = 1
        else:
            level_modifier = 0
        bonus = int((base_damage + damage_modifier) * (level + level_modifier))
        if bonus:
            bonus = random.randint(1, bonus)
            if alert_string:
                party1.alert(alert_string.format(bonus), level=party1.verbosity[skill])
    return bonus
    
def process_critical_hit(party1, critical_hit_level, focus1, focus2):
    return process_skill(party1, critical_hit_level, "critical hit", "focus", 
                         focus1, focus2, 15, 13.2, "critical hit for {} extra damage!")
        
def process_strength(party1, strength_level, focus1, focus2):
    return process_skill(party1, strength_level, "strength", "super strength",
                         focus1, focus2, 100, 1, '')
                         
def process_dot(party1, dot_level, focus1, focus2):
    return process_skill(party1, dot_level, "dot", "intensity", 
                         focus1, focus2, 30, 3.3, "DoT effect deals {}")
                        
def process_soak(party2, soak_level, focus1, focus2):
    return process_skill(party2, soak_level, "soak", "dauntless",
                         focus1, focus2, 100, 1, '')
    
def process_dodge(party2, dodge_level, focus1, focus2):
    return process_skill(party2, dodge_level, "dodge", "celerity",
                         focus1, focus2, 66, 1.5, "Dodged {} damage")
    
def process_regen(party2, regen_level, focus1, focus2):
    return process_skill(party2, regen_level, "regen", "adrenaline",
                         focus1, focus2, 30, 3.3, "Regenerated {} health")
    
def process_elements(party1, party2):
    element1 = party1.element
    element2 = party2.element
    element_modifier = 1
    if ELEMENT_BONUS[element1] == element2:
        element_modifier = 1.5
        if element_modifier:
            party1.alert("Dealt {} bonus elemental damage".format(element_modifier),
                         level=party1.verbosity["elemental_damage"])
    elif ELEMENT_PENALTY[element1] == element2:
        element_modifier = .5
        if element_modifier:
            party1.alert("Element damage penalty: {}".format(element_modifier),
                         level=party2.verbosity["elemental_damage_penalty"])
    return element_modifier
    
def process_attack(party1, party2):    
    party1.alert("Attack!", level=party1.verbosity["attack"])
    party1_attack = party1.skills.combat.attack
    focus1 = party1.skills.combat.focus1    
    focus2 = party2.skills.combat.focus2
        
    damage = random.randint(0, party1.skills.combat.damage)
    
    critical_bonus = process_critical_hit(party1, party1_attack.critical_hit.level, focus1, focus2)
    strength_bonus = process_strength(party1, party1_attack.strength.level, focus1, focus2)        
    dot_bonus = process_dot(party1, party1_attack.dot.level, focus1, focus2)
    
    party2_defense = party2.skills.combat.defense 
    focus1 = party2.skills.combat.focus1
    focus2 = party2.skills.combat.focus2
        
    dodge_modifier = process_dodge(party2, party2_defense.dodge.level, focus1, focus2)
    regeneration = process_regen(party2, party2_defense.regen.level, focus1, focus2)
    soak_modifier = process_soak(party2, party2_defense.soak.level, focus1, focus2)
            
    element_modifier = process_elements(party1, party2)    
    process_damage(party1, party2, damage, critical_bonus, dot_bonus, strength_bonus,
                   dodge_modifier, regeneration, soak_modifier, element_modifier)
                   
def process_damage(party1, party2, damage, critical_bonus, dot_bonus, strength_bonus,
                   dodge_modifier, regeneration, soak_modifier, element_modifier):
    final_damage = max(0, damage + critical_bonus + dot_bonus - dodge_modifier)
    final_damage += strength_bonus
    final_damage = max(0, final_damage - soak_modifier)
    
    final_damage = int(final_damage * element_modifier)
    assert final_damage >= 0
            
    party1.alert("Dealt {} damage".format(final_damage), level=party1.verbosity["dealt damage"])
    party2.alert("Received {} damage".format(final_damage), level=party2.verbosity["received damage"])
    party2.health -= final_damage - regeneration
                            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
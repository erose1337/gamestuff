import random

ELEMENT_BONUS = {"Fire" : "Air", "Air" : "Stone", "Stone" : "Electric", 
                 "Electric" : "Water", "Water" : "Fire", "Excellence" : "None", "Neutral" : "None"}
ELEMENT_PENALTY = dict((value, key) for key, value in ELEMENT_BONUS.items())
del ELEMENT_PENALTY["None"]
ELEMENT_PENALTY["Excellence"] = "None"
ELEMENT_PENALTY["Neutral"] = "None"

    
def process_skill(party1, level, skill, toggle_name, focus1, focus2,
                  activation_chance, base_damage, alert_string,
                  chance_modifier, damage_modifier):
    bonus = 0
    if toggle_name in party1.toggle_abilities:
        chance_modifier = chance_modifier
        damage_modifier = damage_modifier
    else:
        chance_modifier = damage_modifier = 0        
   # print "Rolling: ", party1.name, level, skill, activation_chance + chance_modifier, damage_modifier, level
    if level and random.randint(0, 100) <= activation_chance + chance_modifier:
        if skill in (focus1, focus2):
            level_modifier = 1
        else:
            level_modifier = 0
        bonus = int(damage_modifier + level + level_modifier)
   #     print "     bonus: ", bonus
        if bonus:
            #bonus = random.randint(1, bonus)
            if alert_string:
                party1.alert(alert_string.format(bonus), level=party1.verbosity[skill])
    #if skill in ("soak", "strength") and level:
    #    print skill, bonus
    return bonus
    
def process_critical_hit(party1, critical_hit_level, focus1, focus2):
    return process_skill(party1, critical_hit_level, "critical hit", "focus", 
                         focus1, focus2, 15, 10, "critical hit for {} extra damage!")
        
def process_strength(party1, strength_level, focus1, focus2):
    return process_skill(party1, strength_level, "strength", "super strength",
                         focus1, focus2, 101, 1.5, '')
                         
def process_dot(party1, dot_level, focus1, focus2):
    return process_skill(party1, dot_level, "intensity", "ferocious", 
                         focus1, focus2, 30, 3.3, '')
                        
def process_soak(party2, soak_level, focus1, focus2):
    return process_skill(party2, soak_level, "soak", "dauntless",
                         focus1, focus2, 101, 1.6, '')
    
def process_dodge(party2, dodge_level, focus1, focus2):
    return process_skill(party2, dodge_level, "dodge", "celerity",
                         focus1, focus2, 66, 6.5, "Dodged {} damage")
    
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
       
def process_attack(party1, party2, attack_processor=None):
    assert attack_processor is None
    combat1 = party1.skills.combat
    attack_skills = combat1.attack
    
    focus1 = combat1.focus1
    focus2 = combat1.focus2
    strength_modifier = process_skill(party1, attack_skills.strength.level, "strength",
                                      "super strength", focus1, focus2, 100, 1, '', 0, 0)
    intensity_modifier = process_skill(party1, attack_skills.intensity.level, "intensity",
                                       "ferocious", focus1, focus2, 50, 2, '', 0, 0)
    critical_modifier = process_skill(party1, attack_skills.critical_hit.level, "critical_hit",
                                      "focus", focus1, focus2, 33, 3, "Critical hit for {}", 0, 0)
    damage_roll = strength_modifier + intensity_modifier + critical_modifier
   # print "Damage roll: {}: {}".format(party1.name, damage_roll)
   # print party1.name, attack_skills.strength.level, attack_skills.intensity.level, attack_skills.critical_hit.level, strength_modifier, intensity_modifier, critical_modifier
    combat2 = party2.skills.combat
    defense_skills = combat2.defense
    
    dodge_modifier = process_skill(party2, defense_skills.dodge.level, "dodge",
                                   "celerity", focus1, focus2, 33, 3, "Dodged {} damage", 0, 0)
    regen_modifier = process_skill(party2, defense_skills.regen.level, "regen",
                                   "adrenaline", focus1, focus2, 50, 2, "Regenerated {} health", 0, 0)
    soak_modifier = process_skill(party2, defense_skills.soak.level, "soak",
                                  "dauntless", focus1, focus2, 100, 1, '', 0, 0)  
        
    element_modifier = process_elements(party1, party2)    
    final_damage = max(0, damage_roll - dodge_modifier - soak_modifier)    
    final_damage *= element_modifier   
    
    party1.alert("Dealt {} damage".format(final_damage), level=party1.verbosity["dealt damage"])
    party2.alert("Received {} damage".format(final_damage), level=party2.verbosity["received damage"])
    final_damage = final_damage - regen_modifier
    party2.health -= final_damage    
        
    
def process_skills(party, focus1, focus2, bonuses, skill_processors, skill_object):
    for skill_name, skill_processor in skill_processors:        
        level = getattr(skill_object, skill_name).level
        bonuses["{}_modifier".format(skill_name)] += skill_processor(party, level, focus1, focus2)
            
def process_damage(party1, party2, bonuses, element_modifier):
    damage = random.randint(0, party1.skills.combat.damage) 
    max_hit = damage + bonuses["critical_hit_modifier"] - bonuses["dodge_modifier"]
    #max_hit = (damage + bonuses["critical_hit_modifier"] + bonuses["strength_modifier"] 
    #                  - bonuses["dodge_modifier"] - bonuses["soak_modifier"])
    final_damage = max(0, max_hit)
    final_damage = max(0, final_damage + bonuses["strength_modifier"] - bonuses["soak_modifier"])       
    final_damage = int(final_damage * element_modifier)
    assert final_damage >= 0
            
    party1.alert("Dealt {} damage".format(final_damage), level=party1.verbosity["dealt damage"])
    party2.alert("Received {} damage".format(final_damage), level=party2.verbosity["received damage"])
    party2.health -= final_damage
                            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
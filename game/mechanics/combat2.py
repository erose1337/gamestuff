import random

ELEMENT_BONUS = {"Fire" : "Air", "Air" : "Stone", "Stone" : "Electric", 
                 "Electric" : "Water", "Water" : "Fire", "Excellence" : "None", "Neutral" : "None"}
ELEMENT_PENALTY = dict((value, key) for key, value in ELEMENT_BONUS.items())
del ELEMENT_PENALTY["None"]
ELEMENT_PENALTY["Excellence"] = "None"
ELEMENT_PENALTY["Neutral"] = "None"

def process_attack(party1, party2):    
    party1.alert("Attack!")
    party1_attack = party1.skills.combat.attack
    attack_focus = getattr(party1_attack, "attack_focus", None)
    critical_bonus = dot_bonus = 0
    damage = random.randint(0, party1.skills.combat.damage)
    if attack_focus == "strength":
        bonus = 1
    else:
        bonus = 0
    if "super strength" in party1.toggle_abilities:
        strength_modifier = 2
    else:
        strength_modifier = 1
    strength_bonus = (party1_attack.strength.level + bonus) * strength_modifier
        
    if "focus" in party1.toggle_abilities:
        print "Focus active!"
        chance_modifier = 15
    else:
        chance_modifier = 0
    if random.randint(0, 100) <= 15 + chance_modifier:
        if attack_focus == "critical_hit":
            bonus = 1
        else:
            bonus = 0
        critical_bonus = int(6.6 * (party1_attack.critical_hit.level + bonus))   
        if critical_bonus:
            party1.alert("critical hit for {} extra damage!".format(critical_bonus))
    
    if "intensity" in party1.toggle_abilities:
        chance_modifier = 10
        damage_modifier = 1.5
    else:
        chance_modifier = damage_modifier = 0
        
    if random.randint(0, 100) <= 33 + chance_modifier:
        if attack_focus == "dot":
            bonus = 1
        else:
            bonus = 0
        dot_bonus = int((damage_modifier + 3.3) * (party1_attack.dot.level + bonus))
        if dot_bonus:
            party1.alert("{} for {}".format(party1_attack.dot.hit_string, dot_bonus))
        
    party2_defense = party2.skills.combat.defense  
    defense_focus = getattr(party2_defense, "defense_focus", None)
    
    if defense_focus == "soak":
        bonus = 1
    else:
        bonus = 0
    if "dauntless" in party2.toggle_abilities:
        soak_multiplier = 1 + 1
    else:
        soak_multiplier = 1
    soak_modifier = (party2_defense.soak.level + bonus) * soak_multiplier
    
    if "celerity" in party2.toggle_abilities:
        chance_modifier = 5
        damage_modifier = 1.5
    else:
        chance_modifier = damage_modifier = 0
    dodge_modifier = 0
    if random.randint(0, 100) <= 66 + chance_modifier:
        if defense_focus == "dodge":
            bonus = 1
        else:
            bonus = 0
        dodge_modifier = int((damage_modifier + 1.5) * (party2_defense.dodge.level + bonus))
        if dodge_modifier:
            party2.alert("dodged {} damage!".format(dodge_modifier))
    
    regeneration = 0
    if defense_focus == "regen":
        bonus = 1
    else:
        bonus = 0    
    if "adrenaline" in party2.toggle_abilities:
        chance_modifier = 10
        damage_modifier = 1.5
    else:
        chance_modifier = damage_modifier = 0
    if party2_defense.regen.level + bonus > 0: 
        if random.randint(0, 100) <= 33 + chance_modifier:
            regeneration = int((damage_modifier + 3.3) * (party2_defense.regen.level + 1))            
            if regeneration:                
                party2.alert("Regenerated {} health".format(regeneration))  
    
    final_damage = max(0, damage + critical_bonus + dot_bonus + strength_bonus - soak_modifier - dodge_modifier)
    
    element1 = party1.element
    element2 = party2.element
    element_modifier = 0
    if ELEMENT_BONUS[element1] == element2:
        element_modifier = final_damage / 2
        if element_modifier:
            party1.alert("Dealt {} bonus elemental damage".format(element_modifier))
    elif ELEMENT_PENALTY[element1] == element2:
        element_modifier = -1 * (final_damage / 2)
        if element_modifier:
            party1.alert("Element damage penalty: {}".format(element_modifier))
    final_damage += element_modifier
    assert final_damage >= 0
            
    party1.alert("Dealt {} damage".format(final_damage))
    party2.alert("Received {} damage".format(final_damage))
    party2.health -= final_damage - regeneration
            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
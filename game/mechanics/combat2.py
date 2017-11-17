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
    strength_bonus = party1_attack.strength.level + bonus 

    if random.randint(0, 100) <= 15:
        if attack_focus == "critical_hit":
            bonus = 1
        else:
            bonus = 0
        critical_bonus = int(6.6 * (party1_attack.critical_hit.level + bonus))   
        if critical_bonus:
            party1.alert("critical hit for {} extra damage!".format(critical_bonus))
    
    if random.randint(0, 100) <= 33:
        if attack_focus == "dot":
            bonus = 1
        else:
            bonus = 0
        dot_bonus = int(3.3 * (party1_attack.dot.level + bonus))
        if dot_bonus:
            party1.alert("{} for {}".format(party1_attack.dot.hit_string, dot_bonus))
        
    party2_defense = party2.skills.combat.defense  
    defense_focus = getattr(party2_defense, "defense_focus", None)
    
    if defense_focus == "soak":
        bonus = 1
    else:
        bonus = 0
    soak_modifier = party2_defense.soak.level + bonus
    dodge_modifier = 0
    if random.randint(0, 100) <= 66:
        if defense_focus == "dodge":
            bonus = 1
        else:
            bonus = 0
        dodge_modifier = int(1.5 * (party2_defense.dodge.level + bonus))
        if dodge_modifier:
            party2.alert("dodged {} damage!".format(dodge_modifier))
    
    regeneration = 0
    if defense_focus == "regen":
        bonus = 1
    else:
        bonus = 0    
    if party2_defense.regen.level + bonus > 0: 
        if random.randint(0, 100) <= 33:
            regeneration = int(3.3 * (party2_defense.regen.level + 1))            
            if regeneration:
                party2.health += regeneration
                party2.alert("Regenerated {} health".format(regeneration))  
    
    final_damage = max(0, damage + critical_bonus + dot_bonus + strength_bonus - soak_modifier - dodge_modifier)
    
    element1 = party1.element
    element2 = party2.element
    element_modifier = 0
    if ELEMENT_BONUS[element1] == element2:
        element_modifier = final_damage / 2
        party1.alert("Dealt {} bonus elemental damage".format(element_modifier))
    elif ELEMENT_PENALTY[element1] == element2:
        element_modifier = -1 * (final_damage / 2)
        party1.alert("Element damage penalty: {}".format(element_modifier))
    final_damage += element_modifier
    assert final_damage >= 0
        
    party2.health -= final_damage - regeneration
    party1.alert("Dealt {} damage".format(final_damage))
    party2.alert("Received {} damage".format(final_damage))
      
            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
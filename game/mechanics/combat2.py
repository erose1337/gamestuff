import random

def process_attack(party1, party2):    
    party1.alert("Attack!")
    party1_attack = party1.skills.combat.attack
    
    critical_bonus = dot_bonus = 0
    damage = random.randint(0, party1.skills.combat.damage)
    strength_bonus = party1_attack.strength.level   

    if random.randint(0, 100) <= 15:
        critical_bonus = int(6.6 * party1_attack.critical_hit.level)   
        if critical_bonus:
            party1.alert("critical hit for {} extra damage!".format(critical_bonus))
    
    if random.randint(0, 100) <= 33:
        dot_bonus = int(3.3 * party1_attack.dot.level)
        if dot_bonus:
            party1.alert("{} for {}".format(party1_attack.dot.hit_string, dot_bonus))
        
    party2_defense = party2.skills.combat.defense    
    soak_modifier = party2_defense.soak.level
    dodge_modifier = 0
    if random.randint(0, 100) <= 66:
        dodge_modifier = int(1.5 * party2_defense.dodge.level)
        if dodge_modifier:
            party2.alert("dodged {} damage!".format(dodge_modifier))
    
    regeneration = 0
    if party2_defense.regen.level > 0: 
        if random.randint(0, 100) <= 33:
            regeneration = int(3.3 * party2_defense.regen.level)            
            if regeneration:
                party2.health += regeneration
                party2.alert("Regenerated {} health".format(regeneration))  
                
    final_damage = max(0, damage + critical_bonus + dot_bonus + strength_bonus - soak_modifier - dodge_modifier - regeneration)
    party2.health -= final_damage
    party1.alert("Dealt {} + {} + {} = {} damage".format(damage, critical_bonus, dot_bonus, final_damage))
    party2.alert("Received {} + {} + {} = {} damage".format(damage, critical_bonus, dot_bonus, final_damage))
      
            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
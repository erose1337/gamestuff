import random

def process_attack(party1, party2):    
    party1.alert("Attack!")
    party1_attack = party1.skills.combat.attack
    
    critical_bonus = dot_bonus = 0
    damage = party1.skills.combat.damage
    damage += party1_attack.strength.level   
    if random.randint(0, 100) <= 15:
        critical_bonus = int(damage * party1_attack.critical_hit.level * .66)   
        if critical_bonus:
            party1.alert("critical hit!")
    
    if random.randint(0, 100) <= 33:
        dot_bonus = int(damage * party1_attack.dot.level * .3)
        if dot_bonus:
            party1.alert("{} for {}".format(party1_attack.dot.hit_string, dot_bonus))
        
    party2_defense = party2.skills.combat.defense    
    soak_modifier = party2_defense.soak.level
    if random.randint(0, 100) <= 66:
        dodge_modifier = int(damage * party2_defense.dodge.level * .15)
        if dodge_modifier:
            party2.alert("dodge!")
    else:
        dodge_modifier = 0
        
    final_damage = damage + critical_bonus + dot_bonus - soak_modifier - dodge_modifier
    party2.health -= final_damage
    party1.alert("Dealt {} + {} + {} = {} damage".format(damage, critical_bonus, dot_bonus, final_damage))
    party2.alert("Received {} + {} + {} = {} damage".format(damage, critical_bonus, dot_bonus, final_damage))
    if not party2.is_dead and party2_defense.regen.level > 0: # not dead
        if random.randint(0, 100) <= 33:
            regeneration = int(party2.skills.combat.health.max_health * .03 * party2_defense.regen.level)            
            if regeneration:
                party2.health += regeneration
                party2.alert("Regenerated {} health".format(regeneration))        
            
def process_flee(party1, party2):
    if random.randint(0, 100) <= 50:        
        process_attack(party2, party1)
        return False
    else:
        return True
import game.mechanics.randomgeneration

DEFAULT_HIT_CHANCE = 1
HIT_THRESHOLD = 1

def calculate_attack_rating(character):    
    skill_tree, weapon_type = character.body.hand.weapon_type    
    skill_level = getattr(getattr(character.skills, skill_tree), weapon_type)    
    return skill_level + character.attributes.attack_rating.value
    
def calculate_dodge_chance(character):
    stats = character.stats    
    luck = stats.luck
    return stats.agility.dodge_bonus + stats.wits.dodge_bonus + luck.dodge_bonus + character.attributes.dodge.value
    
def calculate_chance_to_hit(character, other_character):
    # factors in chance to hit: attack skill, dodge chance, luck
    attack_rating = calculate_attack_rating(character)    
    return DEFAULT_HIT_CHANCE + attack_rating - calculate_dodge_chance(other_character)
    
def calculate_soak(character):
    stats = character.stats
    return stats.endurance.level.value + stats.willpower.level.value + character.attributes.soak.value
        
def calculate_damage_output(character, other_character):
    # factors in damage: weapon damage, strength bonus, soak amount, luck    
    weapon_damage = character.weapon.damage
    return (game.mechanics.randomgeneration.random_from_range(*weapon_damage) + 
            character.stats.strength.level.value) #- calculate_soak(other_character)
            
def process_attack(character, other_character):
    #chance_to_hit = calculate_chance_to_hit(character, other_character)    
    #print("Chance to hit: {} / {}".format(chance_to_hit, HIT_THRESHOLD))
    #if chance_to_hit >= HIT_THRESHOLD:
    damage_output = calculate_damage_output(character, other_character)
    other_character.stats.health.current_health -= damage_output
    
    character.stats.strength.level.progress += damage_output
    
    skill_tree, weapon_type = character.body.hand.equipment.weapon_type    
    melee = getattr(character.skills, skill_tree)        
    skill = getattr(melee, weapon_type)        
    character.alert("Got xp in: {} and {}".format(melee.level, skill.level))
    print character.skills, character.skills.level
    melee.level.progress += damage_output    
    skill.level.progress += damage_output
    
def process_flee(fleeing_character, other_character):
    if game.mechanics.randomgeneration.random_from_range(25, 100) <= 25:
        return False
    else:
        return True
            
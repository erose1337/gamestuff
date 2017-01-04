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
    return stats.endurance + stats.willpower + character.attributes.soak
        
def calculate_damage_output(character, other_character):
    # factors in damage: weapon damage, strength bonus, soak amount, luck    
    weapon_damage = character.body.hand.damage
    return (random_selection(*weapon_damage) + character.stats.strength.level) - calculate_soak(other_character)
            
def process_attack(character, other_character):
    chance_to_hit = calculate_chance_to_hit(character, other_character)    
    if chance_to_hit >= HIT_THRESHOLD:
        other_character.stats.health -= calculate_damage_output(character, other_character)
    
        
import game.items

WEAPON_TYPES = ("unarmed", "knife", "sword", "axe", "polearm")

class Melee_Weapon(game.items.Weapon):    

    defaults = {"weapon_type" : ("Melee_Weapon", "melee"), "quality" : 0.0, "damage" : (0, 0)}
    

class Unarmed(Melee_Weapon):
        
    defaults = {"weapon_type" : ("unarmed", "melee"), "damage" : (0, 1)}
    
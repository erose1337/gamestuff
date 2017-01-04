import game.items

WEAPON_TYPES = ("Unarmed", "Knife", "Sword", "Axe", "Polearm")

class Weapon_Part(game.items.Component): pass


class Melee_Weapon(game.items.Weapon):    

    defaults = {"weapon_type" : ("Melee", "")}
    

class Unarmed(Melee_Weapon):
        
    defaults = {"weapon_type" : ("Melee", "Unarmed"), "damage" : (0, 1)}
           
                                
class Knife(Melee_Weapon):
        
    component_pieces = ("handle", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Knife")}
    required_attributes = ("handle", "blade")
    
    class Knife_Handle(Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Knife_Blade(Weapon_Part):
            
        defaults = {"material_type" : "iron"}
        occupied_slots = ("blade", )
        
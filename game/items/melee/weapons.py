import game.items

WEAPON_TYPES = ("Unarmed", "Knife", "Sword", "Axe", "Polearm")

class Melee_Weapon(game.items.Weapon):    

    defaults = {"weapon_type" : ("Melee", ""), "reach" : 0}
    

class Unarmed(Melee_Weapon):
        
    defaults = {"weapon_type" : ("Melee", "Unarmed"), "damage" : (0, 1), "reach" : 1}
           
                                                              
class Knife(Melee_Weapon):
        
    component_pieces = ("handle", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Knife")}
    required_attributes = ("handle", "blade")
    required_tools_to_assemble = ("hammer", )
    
    class Knife_Handle(game.items.Weapon_Part):
        
        component_pieces = ("resource", )
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Knife_Blade(game.items.Weapon_Part):
            
        component_pieces = ("resource", )
        defaults = {"material_type" : "iron"}
        occupied_slots = ("blade", )
        
        
class Sword(Melee_Weapon):
        
    component_pieces = ("handle", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type": ("Melee", "Sword")}
    requires_attributes = ("handle", "blade")
    
    class Sword_Handle(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Sword_Blade(game.items.Weapon_Part):
        
        defaults = {"material_type" : "iron"}
        occupied_slots = ("blade", )
        
        
class Great_Sword(Melee_Weapon):
            
    component_pieces = ("handle", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Great Sword")}
    requires_attributes = ("handle", "blade")
    
    class Great_Sword_Handle(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Great_Sword_Blade(game.items.Weapon_Part):
        
        defaults = {"material_type" : "iron"}
        occupied_slots = ("blade", )
        
        
class Axe(Melee_Weapon):
            
    component_pieces = ("handle", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Axe")}
    requires_attributes = ("handle", "blade")    
        
    class Axe_Handle(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Axe_Blade(game.items.Weapon_Part):
        
        defaults = {"material_type" : "iron"}
        occupied_slots = ("handle", )
        
        
class Polearm(Melee_Weapon):
            
    component_pieces = ("handle", "shaft", "blade")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Polearm")}
    requires_attributes = ("handle", "shaft", "blade")
    
    class Polearm_Handle(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Polearm_Shaft(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("shaft", )
        
        
    class Polearm_Blade(game.items.Weapon_Part):
        
        defaults = {"material_type" : "iron"}
        occupied_slots = ("blade", )
        
        
class Blunt(Melee_Weapon):
            
    component_pieces = ("handle", "shaft")
    defaults = {"handle" : None, "blade" : None, "weapon_type" : ("Melee", "Blunt")}
    requires_attributes = ("handle", "shaft")
    
    class Blunt_Handle(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Blunt_Shaft(game.items.Weapon_Part):
        
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("shaft", )
        
        
    
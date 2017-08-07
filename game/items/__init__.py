import pride.components.base

class GenericGameActionFailure(Exception): pass

    
class Item(pride.components.base.Base):
    
    defaults = {"name" : '', "size" : 0}
    
            
class Component(Item): 

    defaults = {"material_type" : None}    
    
    def attach_to(self, equipment):
        raise NotImplementedError()            
        
    
class Equipment(Item):  
    
    mutable_defaults = {"effect_modifiers" : list}    
    
    defaults = {"durability" : 100, "equips_to" : tuple()}
        
    component_pieces = tuple()          
    occupied_slots = tuple()
    inherited_attributes = {"occupied_slots" : tuple, "component_pieces" : tuple}
    
    def __init__(self, **kwargs):
        super(Equipment, self).__init__(**kwargs)
        for component_name in self.component_pieces:
            self.add(getattr(self, component_name))
       
    def add(self, component):
        super(Equipment, self).add(component)        
        component.attach_to(self)
        
    def remove(self, component):
        component.unattach_from(self)
        super(Equipment, self).add(component)
        
    @classmethod
    def assemble(cls, **components):
        spaces = list(cls.component_pieces)
        for component in components.values():
            for slot in component.occupied_slots:
                try:
                    spaces.remove(slot)
                except ValueError:
                    raise GenericGameActionFailure()
        else:
            return cls(**components)
            
    def disassemble(self):
        components = []
        for component_name in self.component_pieces:
            component = getattr(self, component_name)
            components.append(component)
            self.remove(component)            
            delattr(self, component_name)
        return components            
        
        
class Weapon(Equipment):
        
    defaults = {"weapon_type" : ("Skill_Tree", "Weapon_Type"), 
                "damage" : (0, 0), "speed" : 1, "equips_to" : ("hand", )}
    
    
class Weapon_Part(Component): 

    defaults = {"damage" : (0, 0), "speed" : 0, "durability" : 0}
    
    def attach_to(self, weapon):
        damage_min, damage_max = weapon.damage
        self_min, self_max = self.damage
        weapon.damage = (self_min + damage_min, self_max + damage_max)
        weapon.speed += self.speed
        weapon.durability += self.durability        
    
import pride.components.base

class GenericGameActionFailure(Exception): pass

    
class Item(pride.components.base.Base):
    
    defaults = {"name" : ''}
    component_pieces = tuple()  
    inherited_attributes = {"component_pieces" : tuple}
    
    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
        for component_name in self.component_pieces:
            self.add(getattr(self, component_name))
       
    def add(self, component):
        super(Item, self).add(component)        
        component.attach_to(self)
        
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

            
class Component(Item): 

    defaults = {"material_type" : None, "stat_modifications" : tuple()}    
    occupied_slots = tuple()
    inherited_attributes = {"occupied_slots" : tuple}
    
    def attach_to(self, equipment):
        raise NotImplementedError()            
        
    
class Equipment(Item):  
    
#    mutable_defaults = {"stat_modifiers" : list}    
    
    defaults = {"durability" : 100}
    
                        
class Weapon(Equipment):
        
    defaults = {"weapon_type" : ("Skill_Tree", "Weapon_Type"), 
                "damage" : (0, 0), "speed" : 1}
    
    
class Weapon_Part(Component): 

    defaults = {"damage" : (0, 0), "speed" : 0, "durability" : 0}
    
    def attach_to(self, weapon):
        damage_min, damage_max = weapon.damage
        self_min, self_max = self.damage
        weapon.damage = (self_min + damage_min, self_max + damage_max)
        weapon.speed += self.speed
        weapon.durability += self.durability        
    
import pride.components.base

class GenericGameActionFailure(Exception): pass

    
class Item(pride.components.base.Base):
    
    defaults = {"name" : ''}
    
    
class Component(Item): 

    defaults = {"material_type" : None, "stat_modifications" : tuple()}    
    occupied_slots = tuple()
    inherited_attributes = {"occupied_slots" : tuple}
    
        
class Equipment(Item):  
    
    mutable_defaults = {"stat_modifiers" : list}    
    component_pieces = tuple()  
    inherited_attributes = {"component_pieces" : tuple}
            
    def __init__(self, **kwargs):
        super(Equipment, self).__init__(**kwargs)
        for component in self.component_pieces:
            setattr(self, component, self.create(getattr(self, component)))
        
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
        
    
class Weapon(Equipment):
        
    defaults = {"weapon_type" : ("Skill_Tree", "Weapon_Type"), "damage" : (0, 0), "speed" : 1}
    
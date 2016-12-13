import pride.components.base

class Item(pride.components.base.Base):
    
    defaults = {"name" : ''}
    
    
class Equipment(Item):  

    defaults = {"quality" : 0.0}
    mutable_defaults = {"stat_modifiers" : list}
               
    
class Weapon(Equipment):
        
    defaults = {"weapon_type" : "", "damage" : (0, 0)}
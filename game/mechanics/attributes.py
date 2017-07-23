import pride.components.base

class Attribute(pride.components.base.Base):    

    defaults = {"value" : 1}
    
  #def __get__(self, instance, owner):        
  #    return self.value
  #    
  #def __set__(self, instance, value):
  #    self.value = value          

    
class Attack_Rating(Attribute): pass
        
        
class Damage(Attribute): pass

        
class Soak(Attribute): pass


class Dodge(Attribute): pass


class Energy(Attribute): pass
            
    
class Attributes(pride.components.base.Base):
            
    defaults = {"all_attributes" : ("Attack_Rating", "Damage", "Soak", "Dodge", "Energy")}
            
    def __init__(self, **kwargs):
        super(Attributes, self).__init__(**kwargs)
        for attribute in self.all_attributes:
            setattr(self, attribute.lower(), self.create("game.mechanics.attributes." + attribute))
            
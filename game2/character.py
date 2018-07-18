import pride.components.base

class Resists(pride.components.base.Base):
    
    resist_names = ("fire", "water", "air", "lightning", "earth", "magic",
                    "poison", "light", "darkness")
    defaults = dict((name, 0) for name in resist_names)

                
class Stats(pride.components.base.Base):
    
    stat_names = ("health", "energy", "recovery", "attack", "defence")
    defaults = dict((name, 0) for name in stat_names)
           
    
#class Ability(pride.components.base.Base):
#        
#    defaults = {"level" : 0, "target" : None, "area" : 0}
    
    
class Abilities(pride.components.base.Base):
                    
    defaults = {"dodge" : 0, "block" : 0,}
    

class Equipment(pride.components.base.Base):
        
    defaults = {"head" : None, "torso" : None, "back" : None,
                "shoulders" : None, "arms" : None, "hands" : None, 
                "waist" : None, "thighs" : None, "legs" : None, "feet" : None,
                "neck" : None, "fingers" : None}
    
class Character(pride.components.base.Base):

    defaults = {"name" : ''}

    mutable_defaults = {"stats" : Stats, "abilities" : Abilities, "equipment" : Equipment,
                        "resists" : Resists}
                
    def save(self):
        return pickle.dumps(self) # todo: Change from pickle
    
    @staticmethod
    def load(data):
        return pickle.loads(self) # todo: Change from pickle
        
                
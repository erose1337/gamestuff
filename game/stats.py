import pride.components.base

import game.level

class Stat(pride.components.base.Base):
    
    defaults = {"_initial_level" : 1, "level" : 1}
    
    def __init__(self, **kwargs):
        super(Stat, self).__init__(**kwargs)
        if self.level is None:
            self.level = self.create(game.level.Level, value=self._initial_level)
        
        
class Strength(Stat): pass


class Agility(Stat): 

    defaults = {"dodge_bonus" : 1}


class Endurance(Stat): pass


class Potency(Stat): pass


class Wits(Stat): 

    defaults = {"dodge_bonus" : 1}


class Willpower(Stat): pass


class Health(Stat): 

    defaults = {"_initial_level" : 10}
    flags = {"_current_health" : 1}
    
    def _get_current_health(self):
        return self._current_health
    def _set_current_health(self, value):
        self._current_health = value
        if value <= 0:
            self.parent.parent.die()
    current_health = property(_get_current_health, _set_current_health)
    
    def __init__(self, **kwargs):
        super(Health, self).__init__(**kwargs)        
        self.current_health = self.level
        
   
class Luck(Stat):
    
    defaults = {"current_luck" : 0, "bonus_luck" : 0, "dodge_bonus" : 1}
    mutable_defaults = {"level" : lambda: game.level.Level(value=1)}    
        
    def __init__(self, **kwargs):
        super(Luck, self).__init__(**kwargs)
        self.current_luck = self.level.value
        
        
class Stats(pride.components.base.Base):
    
    mutable_defaults = {"strength" : Strength, "agility" : Agility, "endurance" : Endurance,
                        "potency" : Potency, "wits" : Wits, "willpower" : Willpower,
                        "health" : Health, "luck" : Luck}
                        
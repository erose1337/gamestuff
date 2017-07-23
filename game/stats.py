import pride.components.base

import game.level

STATS = ("Strength", "Agility", "Endurance",
         "Potency", "Wits", "Willpower",
         "Health", "Luck")
         
DEFAULT_STATS = dict((item, 1) for item in STATS)
         
class Stat(pride.components.base.Base):
    
    defaults = {"progress" : 0}
    
    def __init__(self, **kwargs):
        super(Stat, self).__init__(**kwargs)
        assert not hasattr(self, "level")
        self.level = self.create(game.level.Level, progress=self.progress)
        
        
class Strength(Stat): pass


class Agility(Stat): 

    defaults = {"dodge_bonus" : 1}


class Endurance(Stat): pass


class Potency(Stat): pass


class Wits(Stat): 

    defaults = {"dodge_bonus" : 1}


class Willpower(Stat): pass


class Health(Stat): 

    defaults = {"_initial_level" : 10, "alert_health_changes" : True}
    flags = {"_current_health" : 1}
    verbosity = {"current_health" : 0}
    
    def _get_current_health(self):
        return self._current_health
    def _set_current_health(self, value):   
        if self.alert_health_changes and value != self._current_health:
            self.parent.alert("Health {} -> {} ({})".format(self._current_health, value, value - self._current_health), 
                            level=self.verbosity["current_health"], 
                            display_name=self.parent.name)        
        self._current_health = value        
        if value <= 0:            
            if not self.dead:
                self.dead = True
                self.parent.die()
        else:
            self.dead = False
    current_health = property(_get_current_health, _set_current_health)
    
    def _get_display_values(self):
        return self._current_health, self.level.value
    display_values = property(_get_display_values)
        
    def __init__(self, **kwargs):
        super(Health, self).__init__(**kwargs)        
        self.current_health = self.level.value
        
   
class Luck(Stat):
    
    defaults = {"current_luck" : 0, "bonus_luck" : 0, "dodge_bonus" : 1}
            
    def __init__(self, **kwargs):
        super(Luck, self).__init__(**kwargs)
        self.current_luck = self.level.value
        
        
class Stats(pride.components.base.Base):
    
    mutable_defaults = {"strength" : Strength, "agility" : Agility, "endurance" : Endurance,
                        "potency" : Potency, "wits" : Wits, "willpower" : Willpower,
                        "health" : Health, "luck" : Luck}
                        
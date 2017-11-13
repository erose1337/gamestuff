import random

import pride.components.base

class Skill(object):
            
    def __init__(self, level=1):
        self.level = level
        
class Critical_Hit(Skill): pass
            
class DoT(Skill): 
    
    hit_string = "Unknown DoT effect harms your opponent!"
    
    
class Strength(Skill): pass
            
class Dodge(Skill): pass

class Regen(Skill): pass

class Soak(Skill): pass

class Attack(Skill):
    
    def __init__(self, critical_hit=0, dot=0, strength=0):        
        self.critical_hit = Critical_Hit(critical_hit)
        self.dot = DoT(dot)
        self.strength = Strength(strength) 
        self.level = sum((critical_hit, dot, strength))
        
class Defence(Skill):
            
    def __init__(self, dodge=0, regen=0, soak=0):
        self.dodge = Dodge(dodge)
        self.regen = Regen(regen)
        self.soak = Soak(soak)
        self.level = sum((dodge, regen, soak))
        
class Health(Skill): 
    
    flags = {"_level" : 0}
    
    def _get_level(self):
        return self._level
    def _set_level(self, value):        
        self._level = value
        self.max_health = 100 + (10 * value)
    level = property(_get_level, _set_level)
    

class Combat(Skill):    

    def __init__(self, critical_hit=0, dot=0, strength=0, dodge=0, regen=0, soak=0, health=0, damage=1):
        self.attack = Attack(critical_hit, dot, strength)
        self.defence = Defence(dodge, regen, soak) 
        self.health = Health(health)       
        self.damage = damage
        self.level = (self.attack.level + self.defence.level) / 2
        

class Skills(object):
    
    def __init__(self, critical_hit=0, dot=0, strength=0, dodge=0, regen=0, soak=0, health=0, damage=1):
        self.combat = Combat(critical_hit, dot, strength, dodge, regen, soak, health, damage)
             
        
class Character(pride.components.base.Base):
    
    defaults = {"skill_tree_type" : Skills, "name" : '', "npc" : True}    
    verbosity = {"die" : 0}
    flags = {"skills" : None, "_health" : 0}
    
    def _get_health(self):
        return self._health
    def _set_health(self, value):
        self._health = max(value, 0)
        if not self._health:
            self.die()
    health = property(_get_health, _set_health)
    
    def _get_is_dead(self):
        return True if not self._health else False
    is_dead = property(_get_is_dead)
    
    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        if self.skills is None:
            self.skills = self.skill_tree_type(damage=10)
        self.health = 100 + (10 * self.skills.combat.health.level)
        
    def die(self):
        self.alert("Died", level=self.verbosity["die"])
        
    def alert(self, message, level=0, display_name=None):
        if display_name is None:
            display_name = self.name
        super(Character, self).alert(message, level=level, display_name=display_name)
        
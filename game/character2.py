import random
import pickle # todo: use prides save feature instead

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
        
    
class Defense(Skill):
            
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
        self.defense = Defense(dodge, regen, soak) 
        self.health = Health(health)       
        self.damage = damage
        self.level = (self.attack.level + self.defense.level) / 2
        

class Skills(object):
    
    def __init__(self, critical_hit=0, dot=0, strength=0, dodge=0, regen=0, soak=0, health=0, damage=1):
        self.combat = Combat(critical_hit, dot, strength, dodge, regen, soak, health, damage)                
        
    @classmethod
    def random_skills(cls, level):
        defense_points = attack_points = level
        kwargs = {"critical_hit" : 0, "dot" : 0, "strength" : 0,
                  "dodge" : 0, "regen" : 0, "soak" : 0}
        for point in range(attack_points):
            random_skill = random.choice(("critical_hit", "dot", "strength"))
            kwargs[random_skill] += 1
        for point in range(defense_points):
            random_skill = random.choice(("dodge", "regen", "soak"))
            kwargs[random_skill] += 1
        kwargs["health"] = level
        kwargs["damage"] = 10 + level
        combat = Combat(**kwargs)
        
        
class Character(pride.components.base.Base):
    
    defaults = {"skill_tree_type" : Skills, "name" : '', "npc" : True, "skills" : None,
                "element" : "Neutral"}    
    verbosity = {"die" : 0}
    flags = {"_health" : 0, "_xp" : 0}
    mutable_defaults = {"complete_quests" : set, "toggle_abilities" : list}
    
    def _get_health(self):
        return self._health
    def _set_health(self, value):
        value = min(value, self.skills.combat.health.max_health)
        self._health = max(value, 0)
        if not self._health:
            self.die()
    health = property(_get_health, _set_health)
    
    def _get_max_health(self):
        return self.skills.combat.health.max_health
    max_health = property(_get_max_health)
    
    def _get_is_dead(self):
        return True if not self._health else False
    is_dead = property(_get_is_dead)
    
    def _get_xp(self):
        return self._xp
    def _set_xp(self, value):        
        self._xp = value
        if self._xp > 10 ** (self.skills.combat.level + 1):            
            self.level_up()
    xp = property(_get_xp, _set_xp)
    
    def __init__(self, *args, **kwargs):        
        super(Character, self).__init__(*args, **kwargs)
        if self.skills is None:                        
            self.skills = self.skill_tree_type(damage=10)
        self.health = 100 + (10 * self.skills.combat.health.level)
        self.name += " ({})".format(self.element)
        
    def die(self):
        self.alert("Died", level=self.verbosity["die"])
        
    def alert(self, message, level=0, display_name=None):
        if display_name is None and hasattr(self, "name"):
            display_name = self.name
        super(Character, self).alert(message, level=level, display_name=display_name)
        
    def level_up(self):
        skills = self.skills.combat
        assert isinstance(skills, Combat)
        skills.level += 1
        skills.damage += 1
        skills.health.level += 1
        self.alert("Level increased to {}".format(skills.level))
        attack_skills = skills.attack
        assert isinstance(attack_skills, Attack)
        defense_skills = skills.defense
        assert isinstance(defense_skills, Defense)
        attack_focus = attack_skills.attack_focus
        defense_focus = defense_skills.defense_focus
        
        attack_skill = getattr(attack_skills, attack_focus)
        defense_skill = getattr(defense_skills, defense_focus)
        
        attack_skill.level += 1
        defense_skill.level += 1
        self.alert("{} increased to level {}".format(attack_focus, attack_skill.level))
        self.alert("{} increased to level {}".format(defense_focus, defense_skill.level))
        
    def save(self):
        return pickle.dumps(self)
        
    @staticmethod
    def load(data):
        return pickle.loads(data)
        
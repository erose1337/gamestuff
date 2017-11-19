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

    def __init__(self, critical_hit=0, dot=0, strength=0, dodge=0, 
                 regen=0, soak=0, health=0, damage=1, focus1=None, focus2=None):
        self.attack = Attack(critical_hit, dot, strength)
        self.defense = Defense(dodge, regen, soak) 
        self.health = Health(health)       
        self.damage = damage
        self.level = (self.attack.level + self.defense.level) / 2
        self.focus1 = focus1
        self.focus2 = focus2

        
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
    flags = {"_health" : 0, "_xp" : 0, "_combat_points" : 0}
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
    
    def _get_combat_points(self):
        return self._combat_points
    def _set_combat_points(self, value):
        value = min(value, self.skills.combat.level * 2)
        self._combat_points = max(value, 0)        
        if not self._combat_points and self.toggle_abilities:
            self.alert("ran out of combat points, toggles disabled!")
            self.toggle_abilities = []
    combat_points = property(_get_combat_points, _set_combat_points)
        
    def _get_max_combat_points(self):
        return self.skills.combat.level * 2
    max_combat_points = property(_get_max_combat_points)
    
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
       # self.name += " ({})".format(self.element)
        
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
        focus1 = skills.focus1
        focus2 = skills.focus2
                
        try:
            skill1 = getattr(attack_skills, focus1)
        except AttributeError:
            skill1 = getattr(defense_skills, focus2)
            
        try:
            skill2 = getattr(attack_skills, focus2)
        except AttributeError:
            skill2 = getattr(defense_skills, focus2)
            
        skill1.level += 1
        skill2.level += 1
        self.alert("{} increased to level {}".format(focus1.replace('_', ' '), skill1.level))
        self.alert("{} increased to level {}".format(focus2.replace('_', ' '), skill2.level))
        
    def save(self):
        return pickle.dumps(self)
        
    @staticmethod
    def load(data):
        return pickle.loads(data)
        
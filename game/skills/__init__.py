import pride.components.base

import game.level
import game.items.melee.weapons
import game.items.range.weapons
import game.items.magic.weapons
    
class Major_Skill(pride.components.base.Base):
    
    defaults = {"level" : None, "_initial_progress" : 0,
                "minor_skills" : tuple()}
    
    
    def __init__(self, **kwargs):
        super(Major_Skill, self).__init__(**kwargs)
        assert self.level is None
       # self.level = game.level.Level(progress=self._initial_progress)
        for skill_type in self.minor_skills:                       
            setattr(self, skill_type.__name__, self.create(skill_type))
            
            
class Minor_Skill(pride.components.base.Base):
                
    defaults = {"level" : None, "_initial_progress" : 0}
    
    def __init__(self, *args, **kwargs):
        super(Minor_Skill, self).__init__(*args, **kwargs)
        assert self.level is None
        self.level = game.level.Level(progress=self._initial_progress)
        
    
class Melee(Major_Skill): 

    defaults = {"minor_skills" : (type(name, (Minor_Skill, ), {}) for name in game.items.melee.weapons.WEAPON_TYPES)}
        
    
class Range(Major_Skill): 

    defaults = {"minor_skills" : (type(name, (Minor_Skill, ), {}) for name in game.items.range.weapons.WEAPON_TYPES)}


class Magic(Major_Skill): 

    defaults = {"minor_skills" : (type(name, (Minor_Skill, ), {}) for name in game.items.magic.weapons.WEAPON_TYPES)}


class Defence(Major_Skill): pass


class Crafting(Major_Skill): pass


class Spellcraft(Major_Skill): pass


class Potions(Major_Skill): pass
    
    
class Skills(pride.components.base.Base):
    
    defaults = {"major_skills" : ("Melee", "Range", "Magic", "Defence",
                                  "Crafting", "Spellcraft", "Potions")}
                
    def __init__(self, **kwargs):
        super(Skills, self).__init__(**kwargs)
        for skill in self.major_skills:
            setattr(self, skill, self.create("game.skills." + skill))
            
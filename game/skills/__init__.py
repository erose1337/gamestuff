import pride.components.base

import game.level
import game.items.melee.weapons
import game.items.range.weapons
import game.items.magic.weapons
    
class Skill(pride.components.base.Base):
    
    defaults = {"level" : None, "_initial_level" : 1,
                "sub_skills" : tuple()}
    
    def __init__(self, **kwargs):
        super(Skill, self).__init__(**kwargs)
        if self.level is None:
            self.level = game.level.Level(value=self._initial_level)
        for skill in self.sub_skills:            
            setattr(self, skill, self.create(game.level.Level, value=self._initial_level))
            
    
class Melee(Skill): 

    defaults = {"sub_skills" : game.items.melee.weapons.WEAPON_TYPES}
        
    
class Range(Skill): 

    defaults = {"sub_skills" : game.items.range.weapons.WEAPON_TYPES}


class Magic(Skill): 

    defaults = {"sub_skills" : game.items.magic.weapons.WEAPON_TYPES}


class Defence(Skill): pass


class Crafting(Skill): pass


class Spellcraft(Skill): pass


class Potions(Skill): pass
    
    
class Skills(pride.components.base.Base):
    
    defaults = {"all_skills" : ("Melee", "Range", "Magic", "Defence",
                                "Crafting", "Spellcraft", "Potions")}
                
    def __init__(self, **kwargs):
        super(Skills, self).__init__(**kwargs)
        for skill in self.all_skills:
            setattr(self, skill, self.create("game.skills." + skill))
            
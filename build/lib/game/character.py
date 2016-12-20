import pride.components.base                

import stats
import skills
import skills.melee
import items.backpack
import items.melee.weapons
import mechanics.attributes
import mechanics.combat
                
    
BODY_PARTS = ("head", "face", "neck", "shoulder", "chest", "back",
              "arm", "wrist", "hand", "waist", "thigh", "leg", "foot",                                 
              "finger", "tattoo", "hand")
                                
class Body_Part(pride.components.base.Base):
        
    defaults = {"value" : None}
    
    def __get__(self, instance, owner):                
        return self.value
        
    def __set__(self, instance, value):
        self.value = value
        

class Head(Body_Part): pass
class Face(Body_Part): pass
class Neck(Body_Part): pass
class Shoulder(Body_Part): pass
class Chest(Body_Part): pass
class Back(Body_Part): pass
class Arm(Body_Part): pass
class Wrist(Body_Part): pass
class Hand(Body_Part): pass
class Waist(Body_Part): pass
class Thigh(Body_Part): pass
class Leg(Body_Part): pass
class Foot(Body_Part): pass
class Hand(Body_Part): pass
class Finger(Body_Part): pass
class Tattoo(Body_Part): pass


class Hand(Body_Part):
        
    def _get_weapon_type(self):
        value = self.value        
        if value is None:
            strength = self.parent.parent.stats.strength.level
            value = items.melee.weapons.Unarmed(damage=(strength / 4, strength))
        return value.weapon_type
    weapon_type = property(_get_weapon_type)
        
    
class Body(pride.components.base.Base):
    
    defaults = {"body_parts" : ("head", "face", "neck", "shoulder", "chest", "back",
                                "arm", "wrist", "hand", "waist", "thigh", "leg", "foot",                                 
                                "finger", "tattoo", "hand"),
                "backpack_type" : "items.backpack.No_Backpack"}    
    
    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        for body_part in self.body_parts:            
            setattr(self, body_part, self.create("game.character." + body_part[0].upper() + body_part[1:]))        
        self.backpack = self.create(self.backpack_type)    
    
    
class Character(pride.components.base.Base):
    
    defaults = {"name" : ''}  
    flags = {"_attack_bonus" : 0}
    verbosity = {"die" : 0}
               
    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)
        self.stats = self.create(stats.Stats)
        self.skills = self.create(skills.Skills)        
        self.attributes = self.create(mechanics.attributes.Attributes)
        self.body = self.create(Body)
        
    def die(self):
        self.alert("Died", level=self.verbosity["die"])
                
    def equip(self, equipment):
        for attribute, modifier, value in equipment.stat_modifiers:
            getattr(self, attribute).__dict__[modifier] += value
            
    def unequip(self, equipment):
        for attribute, modifier, value in equipment.stat_modifiers:
            getattr(self, attribute).__dict__[modifier] -= value
            
def test_Character():
    character = Character(name="Character unit test")    
    character.stats.strength.level += 1
    
    character2 = Character(name="unit test2")
    
    mechanics.combat.process_attack(character, character2)
    
if __name__ == "__main__":
    test_Character()
    
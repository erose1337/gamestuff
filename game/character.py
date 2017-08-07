import pride.components.base                

import game.stats
import game.skills
import game.items.backpack
import game.items.melee.weapons
import game.mechanics.attributes
import game.mechanics.combat
           
BODY_PARTS = ("head", "face", "neck", "shoulder", "chest", "back",
              "arm", "wrist", "hand", "waist", "thigh", "leg", "foot",                                 
              "finger", "tattoo", "hand")
                                
class Body_Part(pride.components.base.Base):
        
    defaults = {"equipment" : None}
        
class Head(Body_Part): pass
class Face(Body_Part): pass
class Neck(Body_Part): pass
class Shoulder(Body_Part): pass
class Chest(Body_Part): pass
class Back(Body_Part): pass
class Arm(Body_Part): pass
class Wrist(Body_Part): pass
class Hand(Body_Part): 
    
    mutable_defaults = {"equipment" : game.items.melee.weapons.Unarmed}
    
    
class Waist(Body_Part): pass
class Thigh(Body_Part): pass
class Leg(Body_Part): pass
class Foot(Body_Part): pass           
class Finger(Body_Part): pass
class Tattoo(Body_Part): pass        
    
    
class Body(pride.components.base.Base):
    
    defaults = {"body_parts" : ("head", "face", "neck", "shoulder", "chest", "back",
                                "arm", "wrist", "hand", "waist", "thigh", "leg", "foot",                                 
                                "finger", "tattoo"),
                "backpack_type" : "game.items.backpack.No_Backpack",
                "_character" : ''}    
    
    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        _character = self._character
        for body_part in self.body_parts:            
            setattr(self, body_part, self.create("game.character." + body_part[0].upper() + body_part[1:],
                                                 _character=_character))        
        self.backpack = self.create(self.backpack_type)    
    
    
class Character(pride.components.base.Base):
    
    
    defaults = {"name" : '', "npc" : True, "default_backpack" : "game.items.backpack.Purse"}  
    flags = {"_attack_bonus" : 0, "_weapon" : None}
    verbosity = {"die" : 0}
               
    def _get_weapon(self):
        value = self._weapon             
        if value is None:
            strength = self.stats.strength.level.value
            value = game.items.melee.weapons.Unarmed(damage=(strength / 4, strength))        
        return value
    def _set_weapon(self, value):
        self._weapon = value
    weapon = property(_get_weapon, _set_weapon)
    
    def _get_is_human_player(self):
        return not self.npc
    is_human_player = property(_get_is_human_player)
                
    def _get_is_dead(self):
        return self.stats.health.dead
    is_dead = property(_get_is_dead)
    
    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)
        self.stats = self.create(game.stats.Stats)
        self.skills = self.create(game.skills.Skills)        
        self.attributes = self.create(game.mechanics.attributes.Attributes) 
        _kwargs = {"_character" : self.reference}
        if self.is_human_player:
            _kwargs["backpack_type"] = self.default_backpack        
        self.body = self.create(Body, **_kwargs)                    
            
    def die(self):        
        self.alert("Died", level=self.verbosity["die"], display_name=self.name)
        assert self.is_dead == True
        
    def equip(self, equipment):
        body = self.body
        for slot_name in equipment.equips_to:
            slot = getattr(body, slot_name)
            current_equipment = slot.equipment
            if current_equipment is not equipment:
                self.unequip(current_equipment)
            else:
                break
            slot.equipment = equipment
            
        for attribute, modifier, value in equipment.effect_modifiers:
            getattr(self, attribute).__dict__[modifier] += value
            
    def unequip(self, equipment):            
        body = self.body
        for slot_name in equipment.equips_to:
            getattr(body, slot_name).equipment = None    
        for attribute, modifier, value in equipment.effect_modifiers:
            getattr(self, attribute).__dict__[modifier] -= value
    
    def alert(self, message, level=0, display_name=None):
        super(Character, self).alert(message, level, display_name or self.name)
        
        
def test_Character():
    character = Character(name="Character unit test")    
    character.stats.strength.level.progress += 10
    
    character2 = Character(name="unit test2")
    
    game.mechanics.combat.process_attack(character, character2)
    
if __name__ == "__main__":
    test_Character()
    
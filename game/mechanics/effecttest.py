"""
player designed actions
target type:
    - self
    - close ("touch" distance)
    - target (ranged attack)
    - [checkbox] area (splash)
    
effect type:       
    - drain stat            
        - i.e. weapon damage, magic damage, elemental damage
    - restore stat  
        - i.e. health restored, action points restored
    - buff stat
        - + temporary hit points, + temporary action points
        
parameters:    
    - potency
        - magnitude of stat modification
        - i.e. min and max damage
    - duration
        - how long the effect lasts
        - [checkbox] permanent
        
auto-calculated cost
    effect_type_base * (potency + target_modifier) * duration * area_modifier    """
import random

import pride.components.base
    
class Effect(pride.components.base.Base):
    
    defaults = {"effect_type" : None, "target_type" : None, "min_magnitude" : 0, "max_magnitude" : 0,
                "duration" : 1, "area_effect" : 1, "target_stat" : "health"}
    required_attributes = ("effect_type", "target_type", "min_magnitude", "max_magnitude", "duration", "area_effect")    
    allowed_values = {"effect_type" : ("drain", "restore", "buff"),
                      "target_type" : ("self", "close", "range"),
                      "target_stat" : ("health", )}
    
    effect_type_cost = {"drain" : 1, "restore" : 1, "buff" : 1}
    target_type_cost = {"self" : 0, "close" : 1, "range" : 2}
    area_cost = dict((x, x) for x in range(256))
    stat_modifier = {"health" : 1}
    
    def _get_potency(self):
        return int((self.min_magnitude + self.max_magnitude) / 2.0)
    potency = property(_get_potency)
        
    def _get_cost(self):
        effect_type_base = self.effect_type_cost[self.effect_type]
        target_modifer = self.target_type_cost[self.target_type]  
        stat_modifier = self.stat_modifier[self.target_stat]
        area_modifier = self.area_cost[self.area_effect]
        return self.calculate_cost(stat_modifier, effect_type_base, self.potency,
                                   target_modifier, self.duration, area_modifier)
    cost = property(_get_cost)
        
    @staticmethod
    def calculate_cost(stat, effect, potency, target, duration, area):
        return stat * effect * duration * area * (potency + target)
                                      
    def process_effect(self, target):
        if self.duration:
            magnitude = random.randint(self.min_magnitude, self.max_magnitude)
            stat_name = self.target_stat
            stat_value = getattr(target, stat_name)
            self.alert("{} hit for magnitude: {}".format(target.name, magnitude))
            if self.effect_type == "drain":
                magnitude = -magnitude            
            setattr(target, stat_name, stat_value + magnitude)
            self.duration -= 1
            # to do: apply cost        
                        
    
class Drain(Effect):
        
    defaults = {"effect_type" : "drain", "target_type" : "close", "target_stat" : "health",
                "min_magnitude" : 1, "max_magnitude" : 1, "duration" : 1, "area_effect" : 1}
                
    @classmethod
    def unit_test(cls):        
        # "casting" put effects onto a stack
        #   - cost is applied
        # processing each effect:        
        #   - roll damage based on potency
        #   - apply damage
        #   - apply cost
        from game.character2 import Character
                        
        stack = []
        player1 = Character(name="player1")
        player2 = Character(name="player2")
        while True:
            for round in range(4):
                drain1 = cls(max_magnitude=3, duration=1)
                drain2 = cls(duration=2)            
                stack.append((drain1, player2))
                stack.append((drain2, player1))
                new_stack = []
                for effect, target in stack:                    
                    effect.process_effect(target)
                    if target.is_dead:
                        break
                    if effect.duration > 0:
                        assert effect.max_magnitude != 3
                        assert target is not player2
                        new_stack.append((effect, target))
                stack[:] = new_stack
                if target.is_dead:
                    break
            if target.is_dead:
                break
                
if __name__ == "__main__":
    Drain.unit_test()
    
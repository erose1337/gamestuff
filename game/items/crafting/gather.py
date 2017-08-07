import game.items
import game.items.materialquality

class Tool(game.items.Equipment):
            
    defaults = {"tool_type" : ("Crafting", ''), "quality" : 0, "durability" : 0}
    

class Tool_Part(game.items.Component): 

    defaults = {"material_type" : ''}
    
    def _get_quality(self):
        return game.items.materialquality.MATERIAL_QUALITY[self.material_type]
    quality = property(_get_quality)
    
    def _get_durability(self):
        return game.items.materialquality.MATERIAL_DURABILITY[self.material_type]
    durability = property(_get_durability)
    
    def attach_to(self, tool):        
        tool.quality += self.quality
        tool.durability += self.durability
                
    def unattach_from(self, tool):
        tool.quality -= self.quality
        tool.durability -= self.durability
        
        
class Short_Stick(Tool_Part):
           
    defaults = {"material_type" : "driftwood"}
    
    
class Long_Stick(Tool_Part):    

    defaults = {"material_type" : "driftwood"}
    
    
class Sharpstone(Tool_Part):
        
    defaults = {"material_type" : "stone"}
    
    
class Bluntstone(Tool_Part):
        
    defaults = {"material_type" : "stone"}
    
    
class Spearstone(Tool_Part):
        
    defaults = {"material_type" : "stone"}
    
    
class Hammer(Tool):
    
    component_pieces = ("handle", "head")
    defaults = {"handle" : None, "head" : None, "weapon_type" : ("Crafting", "Hammer")}
    required_attributes = ("handle", "head")
    
    class Hammer_Handle(Tool_Part):
                
        defaults = {"material_type" : "driftwood"}
        occupied_slots = ("handle", )
        
        
    class Hammer_Head(Tool_Part):
            
        defaults = {"material_type" : "stone"}
        occupied_slots = ("head", )
        
        
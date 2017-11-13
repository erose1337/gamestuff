import pride.components.base

class GenericGameActionFailure(Exception): pass

    
class Resource(pride.components.base.Base):
        
    defaults = {"material_type" : None, "size" : 0, "item_name" : ''}
    occupied_slots = ("resource", )    
    #inherited_attributes = {"occupied_slots" : tuple}
    
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        if not self.item_name:
            self.item_name = self.__class__.__name__        
        
    def attach_to(self, equipment):
        pass
        #raise NotImplementedError()            
        
    def unattach_from(self, equipment):
        pass
        #raise NotImplementedError()

        
class Item(Resource):
            
    required_tools_to_assemble = tuple()
    
    component_pieces = tuple()                  
    inherited_attributes = {"component_pieces" : tuple}
        
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        for component_name in self.component_pieces:
            self.add(getattr(self, component_name))
            
    @classmethod
    def assemble(cls, **components):
        # make sure all required tools are present
        for tool_type in cls.required_tools_to_assemble:
            try:
                tool = components[tool_type]
            except KeyError:            
                raise GenericGameActionFailure("Failed to assemble {}. Missing required tool {}".format(cls.__name__, tool_type))
            else:
                if tool.tool_type != tool_type:
                    format_args = (cls.__name__, tool.tool_type, tool_type)
                    raise GenericGameActionFailure("Failed to assemble {}. Incompatible tool {} supplied for required {}".format(*format_args))
                    
        # make sure that all the required components were passed as kwargs        
        spaces = list(cls.component_pieces)      # handle, blade                        
        for component in components.values():           
            for slot in component.occupied_slots:  # handle occupies the handle slot              
                try:
                    spaces.remove(slot)          # if the class does not use a handle, then raise
                except ValueError:
                    raise GenericGameActionFailure("Failed to assemble {} using {}".format(cls.__name__, components))
        else:
            return cls(**components)
            
    def disassemble(self):
        components = []
        for component_name in self.component_pieces:
            component = getattr(self, component_name)
            components.append(component)
            self.remove(component)            
            delattr(self, component_name)
        return components  

    @classmethod
    def spawn(cls, *args, **kwargs):
        for component_name in cls.component_pieces:
            if component_name not in kwargs:
                kwargs[component_name] = resolve_string(component_name)()
        return cls(*args, **kwargs)
        
    def add(self, component):
        super(Item, self).add(component)        
        component.attach_to(self)
        
    def remove(self, component):
        component.unattach_from(self)
        super(Item, self).add(component)  

        
class Component(Item): pass  
            
        
class Equipment(Item):  
    
    mutable_defaults = {"effect_modifiers" : list}    
    
    defaults = {"durability" : 100, "equips_to" : tuple()}                  
    
        
class Weapon(Equipment):
        
    defaults = {"weapon_type" : ("Skill_Tree", "Weapon_Type"), 
                "damage" : (0, 0), "speed" : 1, "equips_to" : ("hand", )}
    
    
class Weapon_Part(Component): 

    defaults = {"damage" : (0, 0), "speed" : 0, "durability" : 0}
    
    def attach_to(self, weapon):
        damage_min, damage_max = weapon.damage
        self_min, self_max = self.damage
        weapon.damage = (self_min + damage_min, self_max + damage_max)
        weapon.speed += self.speed
        weapon.durability += self.durability        
    
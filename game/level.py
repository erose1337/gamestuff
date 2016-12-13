import pride.components.base

class Level(pride.components.base.Base):
    
    defaults = {"value" : 1}
    
    def __get__(self, instance, owner):
        return self.value
        
    def __set__(self, instance, value):
        self.value = value
        
    def __add__(self, value):
        return self.value + value
        
    def __sub__(self, value):
        return self.value - value
        
    def __iadd__(self, value):
        self.value += value
        
    def __isub__(self, value):
        self.value -= value
    
import pride.components.base

class CapacityError(BaseException): pass


class Backpack(pride.components.base.Base):
    
    defaults = {"capacity" : 0}
    
    def __init__(self, **kwargs):
        super(Backpack, self).__init__(**kwargs)
        self._storage = []
                
    def __contains__(self, item):
        return item in self._storage
            
    def add(self, item):
        if item.size + sum(_item.size for _item in self._storage) < self.capacity:
            self._storage.append(item)
            super(Backpack, self).add(item)
        else:
            raise CapacityError("Cannot fit item into backpack")
            
    def remove(self, item):        
        self._storage.remove(item)
        super(Backpack, self).remove(item)

        
class No_Backpack(Backpack): 
    
    defaults = {"capacity" : 0}


class Purse(Backpack):
    
    defaults = {"capacity" : 1}
    
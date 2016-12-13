import pride.components.base

class Backpack(pride.components.base.Base):
    
    defaults = {"capacity" : 1}
    
    def __init__(self, **kwargs):
        super(Backpack, self).__init__(**kwargs)
        self._storage = []
                
    def __contains__(self, item):
        return item in self._storage
            
    def store_item(self, item):
        if item.size + sum(_item.size for _item in self._storage) < self.capacity:
            self._storage.append(item)
            
    def remove_item(self, item):        
        self._storage.remove(item)
        

class No_Backpack(Backpack): pass
import pride.gui.gui
import pride.gui.grid

import game.mechanics.random

EARTH_COLOR = (155, 125, 55, 255)

class Tile_Attribute(pride.components.base.Base): 

    defaults = {"classifications" : ((0, "void"), ), "value" : 0}
                    
    def _get_value(self):
        return self._value
    def _set_value(self, value):
        if value < 0:
            value = 0
        self._value = value
    value = property(_get_value, _set_value)
    
    def classify(self):
        value = self.value
        for level, rating in enumerate(self.classifications):
            if value < rating[0]:
                break
        return level, rating
                         
    def process_attribute(self, _neighbor_attribute):  
        attribute = self.value
        neighbor_attribute = _neighbor_attribute.value
        if attribute > neighbor_attribute:
            self_adjustment = -1
            neighbor_adjustment = 1
        elif attribute < neighbor_attribute:
            self_adjustment = 1
            neighbor_adjustment = -1
        else:
            self_adjustment = neighbor_adjustment = 0
        self.value += self_adjustment
        _neighbor_attribute.value += neighbor_adjustment

    def add_noise(self, minimum, maximum):
        self.value += game.mechanics.random.random_from_range(minimum, maximum)
        
def is_water(moisture_level):
    return moisture_level > 128  
        
class Moisture(Tile_Attribute):
    
    defaults = {"classifications" : ((16, "dry"), (32, "low"), (64, "moderate"), (96, "heavy"), (128, "wet")), 
                "value" : 76} 
    
    def process_attribute(self, neighbor_attribute):                       
        self_moisture = self.value
        neighbor_moisture = neighbor_attribute.value
        
        if self_moisture > neighbor_moisture:
            self_adjustment = -1
            neighbor_adjustment = 1
        elif self_moisture < neighbor_moisture:
            self_adjustment = 1
            neighbor_adjustment = -1
        else:
            self_adjustment = neighbor_adjustment = 0
            
        self_elevation = self.parent.elevation.value
        neighbor_elevation = neighbor_attribute.parent.elevation.value
        if (is_water(neighbor_moisture) and self_elevation > neighbor_elevation or 
            is_water(self_moisture) and neighbor_elevation > self_elevation):
            self_adjustment = 0
            neighbor_adjustment = 0  
                    
        self.value += self_adjustment
        neighbor_attribute.value += neighbor_adjustment                 

        
class Temperature(Tile_Attribute):
        
    defaults = {"classifications" : ((32, "freezing"), (64, "cold"), (96, "warm"), (128, "hot"), (256, "scorching")), "value" : 76}

        
class Biology(Tile_Attribute):
            
    defaults = {"classifications" : ((16, "desolate"), (32, "bacteria"), (64, "vegetation"),
                                     (96, "animal"), (128, "overgrown")), "value" : 64}
    

class Elevation(Tile_Attribute):
        
    defaults = {"classifications" : ((32, "subterranean"), (64, "below sea level"), (96, "sea level"), (128, "hills"), (160, "mountains")),
                "value" : 96}
    
    def process_attribute(self, neighbor_attribute):
        pass
        
        
class Pressure(Tile_Attribute): pass


class Light(Tile_Attribute): pass

    
class Game_Tile(pride.gui.gui.Button):
    
    defaults = {"background_color" : EARTH_COLOR,
                "attribute_listing" : (("elevation", Elevation), ("moisture", Moisture))}#, ("temperature", Temperature), 
                                   #    ("pressure", Pressure), ("biology", Biology), ("light", Light))}
    mutable_defaults = {"process_attributes" : list}
    flags = {"overlay" : None}
    
    def __init__(self, **kwargs):
        super(Game_Tile, self).__init__(**kwargs)         
        for name, _type in self.attribute_listing:
            value = self.create(_type)
            setattr(self, name, value)
            self.children.remove(value)
            self.process_attributes.append(name)
            
    def process_neighbor(self, neighbor):        
        for attribute in self.process_attributes:
            self_attribute = getattr(self, attribute)
            neighbor_attribute = getattr(neighbor, attribute)            
            self_attribute.process_attribute(neighbor_attribute)                                                
        
        moisture = self.moisture.value
        if moisture > 96:
            if self.overlay is None:
                self.overlay = self.create(Tile_Overlay)
                self.overlay.pack()
            self.overlay.background_color = (0, 0, moisture, moisture / 2)
        elif self.overlay is not None:
            self.overlay.delete()
            self.overlay = None
            
        
class Tile_Overlay(pride.gui.gui.Button):   

    def left_click(self, mouse):
        return self.parent.left_click(mouse)
        
    
class Map(pride.gui.grid.Grid):
    
    defaults = {"square_colors" : (EARTH_COLOR, ),
                "square_outline_colors" : ((155, 155, 155, 255), ),
                "column_button_type" : Game_Tile,
                "grid_size" : (8, 8)}
        
    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        pride.objects["/Python/Background_Refresh"].callbacks.append((self, "process_grid"))
        
    def process_grid(self):
        for row in range(self.rows):
            for column in range(self.columns):
                cell = self[row][column]
                
                for _index in range(-1, 2):
                    for _index2 in range(-1, 2):
                        try:
                            neighbor = self[row + _index][column + _index2]
                        except IndexError:
                            pass
                        else:
                            cell.process_neighbor(neighbor)        
          
    def randomize(self):                       
        for row in range(self.rows):
            for column in range(self.columns):
                tile = self[row][column]
                for attribute in tile.process_attributes:
                    getattr(tile, attribute).add_noise(-5, 5)
                
from math import log

import pride.gui.gui
import pride.gui.grid

import game.mechanics.randomgeneration

EARTH_COLOR = (155, 125, 55, 255)
WATER_OVERLAY_THRESHOLD = 80

class Tile_Attribute(pride.components.base.Base): 

    defaults = {"classifications" : ((0, "void"), ), "value" : 0, 
                "is_source" : False, "source_magnitude" : 1}
                    
    def _get_value(self):
        return self._value
    def _set_value(self, value):
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self._value = value
    value = property(_get_value, _set_value)
    
    def classify(self):
        value = self.value
        for level, rating in enumerate(self.classifications):
            if value < rating[0]:
                break
        return level, rating
                         
    def process_attribute(self, _neighbor_attribute, coordinates):  
        if self.is_source:            
            self.value += self.source_magnitude
            
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
        self.value += game.mechanics.randomgeneration.random_from_range(minimum, maximum)
        
    def post_process(self):
        pass
        
        
class Moisture(Tile_Attribute):
    
    defaults = {"classifications" : ((16, "dry"), (32, "low"), (64, "moderate"), (96, "heavy"), (128, "wet")), 
                "value" : 76}                

        
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

# log(value, 2) should indicate how far the light should reach
# i.e. 1, 2, 3, 4, 5, 6, 7 tiles away
# < 2 = 

class Light(Tile_Attribute): 

    defaults = {"source_magnitude" : 76, "is_source" : False, "adjustment" : 0, 
                "_amount" : 0, "value" : 0, "dropoff" : 8}    
    
    def process_attribute(self, neighbor_attribute):                             
        self.adjustment = max(self.adjustment, neighbor_attribute.value - self.dropoff)  
        
    def post_process(self):                  
        adjustment = self.adjustment
        if self.is_source:
            self.value = max(self.source_magnitude, adjustment)
        else:
            self.value = adjustment
        self.adjustment = 0            
                
        
class Water_Level(Tile_Attribute): 

    defaults = {"adjustment" : 0, "_amount" : 0}
    
    def process_attribute(self, neighbor_attribute):     
        neighbor_value = neighbor_attribute.value
        self_value = self.value
        if neighbor_value > self_value:
            adjustment = neighbor_value / 8
            neighbor.value -= adjustment
            self.adjustment += adjustment   

    def post_process(self):      
        adjustment = self.adjustment
        self.value += self.adjustment
        self.adjustment = 0
        #self.value += self.adjustment
        #self.adjustment = 0
        #
        #if self.is_source:
        #    self.value += self.source_magnitude  
        #self._amount = self.value / len(self.parent.neighbors)
        
BRIGHTNESS_LEVELS = 64
BRIGHTNESS_SCALAR = 3.0 / BRIGHTNESS_LEVELS
BRIGHTNESS = [BRIGHTNESS_SCALAR * count for count in range(BRIGHTNESS_LEVELS)]#.25, .5, .75, 1.0, 1.25, 1.5, 1.75, 2.0]
BRIGHTNESS_DIVISOR = 256 / BRIGHTNESS_LEVELS
       
class Game_Tile(pride.gui.gui.Button):
    
    defaults = {"background_color" : EARTH_COLOR,
                "attribute_listing" : (("elevation", Elevation), ("water_level", Water_Level), ("light", Light))}#, ("temperature", Temperature), 
                                   #    ("pressure", Pressure), ("biology", Biology), ("light", Light))}
    mutable_defaults = {"process_attributes" : list, "neighbors" : list, "_child_attributes" : list}
    flags = {"overlay" : None}
    
    def __init__(self, **kwargs):        
        super(Game_Tile, self).__init__(**kwargs)                 
        for name, _type in self.attribute_listing:
            value = self.create(_type)                        
            setattr(self, name, value)            
            self.children.remove(value)
            self._child_attributes.append(value)
            self.process_attributes.append(value)
        self.light_overlay = self.create(Tile_Overlay)
        self.light_overlay.background_color = (0, 0, 0, 0)
        self.water_overlay = self.create(Tile_Overlay)
        self.water_overlay.background_color = (0, 0, 0, 0)
        
    def remove(self, item):        
        try:
            super(Game_Tile, self).remove(item)
        except ValueError:
            if item in self._child_attributes:
                self._child_attributes.remove(item)
            else:
                raise                                       
                
    def process_neighbor(self, neighbor):        
        neighbor_processes = neighbor.process_attributes
        for index, attribute_object in enumerate(self.process_attributes):               
            attribute_object.process_attribute(neighbor_processes[index])      
        
        water_level = self.water_level.value
        self.water_overlay.background_color = (0, 5, water_level, water_level)
        #moisture = self.water_level.value
        #if moisture > WATER_OVERLAY_THRESHOLD:
        #    if self.overlay is None:
        #        self.overlay = self.create(Tile_Overlay)
        #        self.overlay.pack()
        #    self.overlay.background_color = (0, 0, moisture, moisture)
        #elif self.overlay is not None:
        #    self.overlay.delete()
        #    self.overlay = None
        
        brightness = self.light.value#BRIGHTNESS[self.light.value / BRIGHTNESS_DIVISOR]        
        self.light_overlay.background_color = (brightness, brightness, brightness, 255)
        #assert self.light_overlay.z == self.z + 1, (self.light_overlay.z, self.z)
        #brightness = self.light.value / 76.0
        #self.background_color = tuple(min(int(color * brightness), 255) for color in EARTH_COLOR)
                
    def post_process(self):
        for attribute in self.process_attributes:
            attribute.post_process()
            
    def delete(self):
        for name, _ in self.attribute_listing:
            getattr(self, name).delete()
        super(Game_Tile, self).delete()
        
        
class Tile_Overlay(pride.gui.gui.Button):   

    defaults = {"pack_mode" : 'z'}
    
    def left_click(self, mouse):
        return self.parent.left_click(mouse)
        
    
class Water_Tile(Tile_Overlay): pass
        
        
class Environment(pride.gui.grid.Grid):
    
    defaults = {"square_colors" : (EARTH_COLOR, ),
                "square_outline_colors" : ((155, 155, 155, 255), ),
                "column_button_type" : Game_Tile,
                "grid_size" : (3, 3), "pack_mode" : "main"}
    
    verbosity = {"setup_cells" : "vvv"}
    
    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)                
        pride.objects["/Python/Background_Refresh"].callbacks.append((self, "process_grid"))  
        self.setup_cells()
        
    def setup_cells(self):
        self.alert("Setting up {} by {} grid".format(*self.grid_size), level=self.verbosity["setup_cells"])
        cells = []
        map = self                       
        for column in range(map.columns):                
            for row in range(map.rows):            
                cell = map[column][row]
                
                for _index in range(-1, 2):
                    for _index2 in range(-1, 2):
                        _column, _row = column + _index, row + _index2
                        if _row < 0 or _column < 0 or (_column, _row) == (column, row):
                            continue
                        try:
                            neighbor = map[_column][_row]
                        except IndexError:
                            pass
                        else:
                            cell.neighbors.append(neighbor)        
                cells.append(cell)
        self.cells = cells        
        
    def process_grid(self):             
        for cell in self.cells:
            for neighbor in cell.neighbors:
                cell.process_neighbor(neighbor)
        for cell in self.cells:
            cell.post_process()                
    
    def randomize(self): 
        return
        map = self
        for row in range(map.rows):
            for column in range(map.columns):
                tile = map[row][column]
                for attribute in tile.process_attributes:
                    attribute.add_noise(-5, 5)
                
    def delete(self):
        self.parent.environment = None
        pride.objects["/Python/Background_Refresh"].callbacks.remove((self, "process_grid"))
        super(Environment, self).delete()              
        
        
class Region(pride.gui.gui.Container):
                    
    defaults = {"recursions" : 3, "minimum_region_size" : 100, "grid_size" : (3, 3),
                "pack_mode" : "left", "region1" : None, "region2" : None, "parent_map" : None,
                "environment" : None, "randomize_environment" : True}

    def subdivide(self):
        self.pack()
        recursions = self.recursions        
        randomize_environment = self.randomize_environment
        if recursions:           
            recursions -= 1
            minimum_size = self.minimum_region_size   
            region1 = None        
            pack_mode = self.pack_mode
            if pack_mode == "top":
                if self.w - minimum_size >= minimum_size:
                    max_width = self.w - minimum_size
                    if max_width == minimum_size:
                        width = minimum_size
                    else:
                        width = game.mechanics.randomgeneration.random_from_range(minimum_size, max_width)
                    pack_mode = "left"                    
                    region1 = self.create(Region, w_range=(width, width), recursions=recursions, pack_mode=pack_mode,
                                                  randomize_environment=randomize_environment, region_number=1,
                                                  parent_map=self.parent_map)                      
            else:
                if self.h - minimum_size >= minimum_size:
                    max_height = self.h - minimum_size
                    if max_height == minimum_size:
                        height = minimum_size
                    else:
                        height = game.mechanics.randomgeneration.random_from_range(minimum_size, max_height)
                    pack_mode = "top"                    
                    region1 = self.create(Region, h_range=(height, height), recursions=recursions, pack_mode=pack_mode,
                                                  randomize_environment=randomize_environment, region_number=1,
                                                  parent_map=self.parent_map)            
            if region1 is not None:                      
                region2 = self.create(Region, recursions=recursions, pack_mode=pack_mode, 
                                              randomize_environment=randomize_environment, 
                                              region_number=2, parent_map=self.parent_map)
                region1.subdivide()
                region2.subdivide()
                self.region1 = region1
                self.region2 = region2                                                             
            else:                   
                self.setup_environment()     
        else:   
            self.setup_environment()                
        
    def setup_environment(self):
        grid_size = game.mechanics.randomgeneration.random_from_range(1, 4), game.mechanics.randomgeneration.random_from_range(1, 4)        
        self.environment = self.create(Environment, grid_size=self.grid_size)
        if self.randomize_environment:                    
            self.environment.randomize()
        self.setup_border_regions() 
        self.parent_map.region_list.append(self)
                
    def setup_border_regions(self): 
        button_type = self.environment.column_button_type
        self.northern_border = self.create(button_type, pack_mode="top", h_range=(10, 10))
        self.southern_border = self.create(button_type, pack_mode="bottom", h_range=(10, 10))
        self.western_border = self.create(button_type, pack_mode="left", w_range=(10, 10))
        self.eastern_border = self.create(button_type, pack_mode="right", w_range=(10, 10))  
                
        map = self.environment
        rows = map.rows
        columns = map.columns
        northern_border = self.northern_border
        southern_border = self.southern_border
        for column in range(columns):
            neighbor = map[column][0]
            northern_border.neighbors.append(neighbor)
            neighbor.neighbors.append(northern_border)
            
            neighbor = map[column][rows - 1]
            southern_border.neighbors.append(neighbor)
            neighbor.neighbors.append(southern_border)
                
        eastern_border = self.eastern_border
        western_border = self.western_border
        for row in range(0, rows):
            neighbor = map[0][row]
            western_border.neighbors.append(neighbor)
            neighbor.neighbors.append(western_border)
            
            neighbor = map[columns - 1][row]
            eastern_border.neighbors.append(neighbor)
            neighbor.neighbors.append(eastern_border)
        
        self.environment.cells.extend((northern_border, southern_border, eastern_border, western_border)) 
          
        
class Map(pride.gui.gui.Window):
            
    defaults = {"region" : None, "randomize_environment" : True}
    mutable_defaults = {"region_list" : list}
    
    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        self.randomize()               
        
    def randomize(self):
        if self.region is not None:
            self.region.delete()        
        region = self.region = self.create(Region, randomize_environment=self.randomize_environment,
                                                   parent_map=self)
        region.subdivide()        
        region.pack() # pack all the environments at the end
        self.link_border_regions()        
        
    def link_border_regions(self):
        region_list = self.region_list
        for region in region_list:            
            for other_region in region_list:
                if region is other_region:
                    continue   
                    
                region_x, region_y = region.position
                region_width = region_x + region.w
                region_height = region_y + region.h
                
                other_x, other_y = other_region.position
                other_width = other_x + other_region.w
                other_height = other_y + other_region.h
                if other_y >= region_y and other_y <= region_height:
                    if region_width == other_x:                        
                        region.eastern_border.neighbors.append(other_region.western_border)
                        other_region.western_border.neighbors.append(region.eastern_border) 
                    elif other_width == region_x:
                        other_region.eastern_border.neighbors.append(region.western_border)
                        region.western_border.neighbors.append(other_region.eastern_border)
                if (other_x >= region_x and other_x <= region_width):
                    if region_height == other_y:                        
                        region.southern_border.neighbors.append(other_region.northern_border)
                        other_region.northern_border.neighbors.append(region.southern_border)
                    elif other_height == region_y:
                        other_region.southern_border.neighbors.append(region.northern_border)
                        region.northern_border.neighbors.append(other_region.southern_border)
                        
            #region.northern_border.neighbors.append(region.western_border)
            #region.northern_border.neighbors.append(region.eastern_border)
            #region.southern_border.neighbors.append(region.western_border)
            #region.southern_border.neighbors.append(region.eastern_border)
            #
            #region.western_border.neighbors.append(region.northern_border)
            #region.western_border.neighbors.append(region.southern_border)
            #region.eastern_border.neighbors.append(region.northern_border)
            #region.eastern_border.neighbors.append(region.southern_border)
            
            
            
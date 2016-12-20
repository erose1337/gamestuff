from math import log

import pride.gui.gui
import pride.gui.grid

import game.mechanics.random

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
        self.value += game.mechanics.random.random_from_range(minimum, maximum)
        
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


class Light(Tile_Attribute): 

    defaults = {"source_magnitude" : 0, "is_source" : True, "value" : 0, "adjustment" : 0,
                "horizontal_direction" : 0, "vertical_direction" : 0}    
    
    def process_attribute(self, neighbor_attribute):     
        amount = self.value / 4
        if (not neighbor_attribute.is_source) or neighbor_attribute.source_magnitude == 0:
            neighbor_attribute.adjustment += amount
        self.adjustment -= amount        

    def post_process(self):                  
        neighbors = len(self.parent.neighbors)
        self.value += self.adjustment - neighbors
        self.adjustment /= neighbors + 1
        
        if self.is_source:
            self.value += self.source_magnitude   
                    
    
class Water_Level(Tile_Attribute): 

    def process_attribute(self, neighbor_attribute):
        self_elevation = self.parent.elevation.value
        neighbor_elevation = neighbor_attribute.parent.elevation.value
        water_level = self.value
        neighbor_water_level = neighbor_attribute.value
        
        adjustment = int(log(abs(water_level - neighbor_water_level) or 1, 2))
        elevation_difference = abs(self_elevation - neighbor_elevation)
        elevation_adjustment = 0
        if elevation_difference:
            elevation_adjustment = int(log(elevation_difference, 3.14))
            adjustment += elevation_adjustment
        #self_adjustment = neighbor_adjustment = 0
        #if self_elevation > neighbor_elevation:
        #    if water_level >= neighbor_water_level:
        #        self_adjustment = -1
        #        neighbor_adjustment = 1
        #elif self_elevation < neighbor_elevation:
        #    if water_level <= neighbor_water_level:
        #        self_adjustment = 1
        #        neighbor_adjustment = -1
        #else:
        if water_level > neighbor_water_level:
            self_adjustment = -adjustment
            neighbor_adjustment = adjustment
        elif water_level < neighbor_water_level:
            self_adjustment = adjustment
            neighbor_adjustment = -adjustment
        else:
            if self_elevation > neighbor_elevation:
                self_adjustment = -elevation_adjustment
                neighbor_adjustment = elevation_adjustment
            elif self_elevation < neighbor_elevation:
                self_adjustment = elevation_adjustment
                neighbor_adjustment = -elevation_adjustment
            else:
                self_adjustment = neighbor_adjustment = 0        
        self.value += self_adjustment
        neighbor_attribute.value += neighbor_adjustment
        
    
class Game_Tile(pride.gui.gui.Button):
    
    defaults = {"background_color" : EARTH_COLOR,
                "attribute_listing" : (("elevation", Elevation), ("water_level", Water_Level), ("light", Light))}#, ("temperature", Temperature), 
                                   #    ("pressure", Pressure), ("biology", Biology), ("light", Light))}
    mutable_defaults = {"process_attributes" : list, "neighbors" : list}
    flags = {"overlay" : None}
    
    def __init__(self, **kwargs):        
        super(Game_Tile, self).__init__(**kwargs)                 
        for name, _type in self.attribute_listing:
            value = self.create(_type)            
            setattr(self, name, value)            
            self.children.remove(value)
            self.process_attributes.append(value)
            
    def process_neighbor(self, neighbor):        
        neighbor_processes = neighbor.process_attributes
        for index, attribute_object in enumerate(self.process_attributes):               
            attribute_object.process_attribute(neighbor_processes[index])      
        
        moisture = self.water_level.value
        if moisture > WATER_OVERLAY_THRESHOLD:
            if self.overlay is None:
                self.overlay = self.create(Tile_Overlay)
                self.overlay.pack()
            self.overlay.background_color = (0, 0, moisture, moisture / 2)
        elif self.overlay is not None:
            self.overlay.delete()
            self.overlay = None

        BRIGHTNESS = [.1, .25, .5, .75, 1.0, 1.25, 1.5, 1.75]
        brightness = BRIGHTNESS[int(log(self.light.value or 1, 4))] 
        #brightness = self.light.value / 76.0
        self.background_color = tuple(min(int(color * brightness), 255) for color in EARTH_COLOR)
                
    def post_process(self):
        for attribute in self.process_attributes:
            attribute.post_process()
            
        
class Tile_Overlay(pride.gui.gui.Button):   

    def left_click(self, mouse):
        return self.parent.left_click(mouse)
        
    
class Water_Tile(Tile_Overlay): pass
        
        
class Environment(pride.gui.grid.Grid):
    
    defaults = {"square_colors" : (EARTH_COLOR, ),
                "square_outline_colors" : ((155, 155, 155, 255), ),
                "column_button_type" : Game_Tile, "grid_type" : "pride.gui.grid.Grid",
                "grid_size" : (3, 3), "pack_mode" : "main"}
        
    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)
        pride.objects["/Python/Background_Refresh"].callbacks.append((self, "process_grid"))  
       # self.map = self.create(self.grid_type, grid_size=self.grid_size, column_button_type=self.column_button_type,
       #                                        square_colors=self.square_colors, square_outline_colors=self.square_outline_colors,
       #                                        pack_mode="main")
        self.setup_cells()
        
    def setup_cells(self):
        cells = []
        map = self
        for row in range(map.rows):
            for column in range(map.columns):
                cell = map[row][column]
                
                for _index in range(-1, 2):
                    for _index2 in range(-1, 2):
                        _row, _column = row + _index, column + _index2
                        if _row < 0 or _column < 0 or (_row, _column) == (row, column):
                            continue
                        try:
                            neighbor = map[_row][_column]
                        except IndexError:
                            pass
                        else:
                            cell.neighbors.append((neighbor, (_row, _column)))        
                cells.append(cell)
        self.cells = cells        
        
    def process_grid(self):
        for cell in self.cells:
            for neighbor, coordinates in cell.neighbors:
                cell.process_neighbor(neighbor)
        for cell in self.cells:
            cell.post_process()                
    
    def randomize(self): 
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
                "pack_mode" : "left", "region1" : None, "region2" : None,
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
                        width = game.mechanics.random.random_from_range(minimum_size, max_width)
                    pack_mode = "left"                    
                    region1 = self.create(Region, w_range=(width, width), recursions=recursions, pack_mode=pack_mode,
                                                  randomize_environment=randomize_environment)                      
            else:
                if self.h - minimum_size >= minimum_size:
                    max_height = self.h - minimum_size
                    if max_height == minimum_size:
                        height = minimum_size
                    else:
                        height = game.mechanics.random.random_from_range(minimum_size, max_height)
                    pack_mode = "top"                    
                    region1 = self.create(Region, h_range=(height, height), recursions=recursions, pack_mode=pack_mode,
                                                  randomize_environment=randomize_environment)            
            if region1 is not None:                      
                region2 = self.create(Region, recursions=recursions, pack_mode=pack_mode, 
                                              randomize_environment=randomize_environment)
                region1.subdivide()
                region2.subdivide()
                self.region1 = region1
                self.region2 = region2
                
                if region1.environment is not None:
                    if region1.pack_mode == "top":
                        region1.southern_border.neighbors.append((region2.northern_border, ("northern", "border")))
                        region2.northern_border.neighbors.append((region1.southern_border, ("southern", "border")))                        
                                                        
                    else:
                        region1.eastern_border.neighbors.append((region2.western_border, ("western", "border")))
                        region2.western_border.neighbors.append((region1.eastern_border, ("eastern", "border")))                        
            else:                   
                self.setup_environment()     
        else:   
            self.setup_environment()

    def setup_environment(self):
        grid_size = self.grid_size
        self.environment = self.create(Environment, grid_size=grid_size)
        if self.randomize_environment:                    
            self.environment.randomize()
        self.setup_border_regions() 
        
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
            northern_border.neighbors.append((neighbor, (column, 0)))
            neighbor.neighbors.append((northern_border, ("northern", "border")))
            
            neighbor = map[column][rows - 1]
            southern_border.neighbors.append((neighbor, (column, rows - 1)))
            neighbor.neighbors.append((southern_border, ("southern", "border")))
                
        eastern_border = self.eastern_border
        western_border = self.western_border
        for row in range(0, rows):
            neighbor = map[0][row]
            western_border.neighbors.append((neighbor, (0, row)))
            neighbor.neighbors.append((western_border, ("western", "border")))
            
            neighbor = map[columns - 1][row]
            eastern_border.neighbors.append((neighbor, (columns - 1, row)))
            neighbor.neighbors.append((eastern_border, ("eastern", "border")))            
        
        self.environment.cells.extend((northern_border, southern_border, eastern_border, western_border)) 
        
        
class Map(pride.gui.gui.Window):
            
    defaults = {"region" : None, "randomize_environment" : True}
    
    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        self.randomize()
        
    def randomize(self):
        if self.region is not None:
            self.region.delete()        
        region = self.region = self.create(Region, randomize_environment=self.randomize_environment)
        region.subdivide()        
        region.pack() # pack all the environments at the end
        
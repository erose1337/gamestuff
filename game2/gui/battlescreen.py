import pride.gui.gui


class Stat_Displayer(pride.gui.gui.Container):
    
    defaults = {"character" : None}
    required_attributes = ("character", )
    post_initializer = "create_display"
    
    def create_display(self):                        
        character = pride.objects[self.character]
        self.create("pride.gui.gui.Container", text=character.name, pack_mode="top")
        
        stats = character.stats               
        for name in stats.stat_names:
            row = self.create("pride.gui.gui.Container", pack_mode="top")            
            row.create("pride.gui.gui.Container", text=name, pack_mode="left")            
            row.create("pride.gui.gui.Container", text=str(getattr(stats, name)), pack_mode="left")
            #row.create("pride.gui.gui.Container", text='+', pack_mode="right", w_range=(0, 20)) # placeholder for now
            
    
class Stat_Container(pride.gui.gui.Container):
    
    defaults = {"stat_displayer_type" : Stat_Displayer, "characters" : tuple()}
    required_attributes = ("characters", )    
    post_initializer = "create_stat_displays"
    
    def create_stat_displays(self):
        for character in self.characters:
            self.create(self.stat_displayer_type, pack_mode="top", character=character)
        

class Action_Menu(pride.gui.gui.Container):
            
    defaults = {"h_range" : (0, 40)}
    post_initializer = "create_selections"
    
    def create_selections(self):
        pass
        

class Battleground(pride.gui.gui.Container):
        
    defaults = {"grid_size" : (5, 5), "characters" : tuple()}
    required_attributes = ("characters", )
    post_initializer = "create_grid"
    
    def create_grid(self):
        grid = self.create("pride.gui.grid.Grid", grid_size=(self.grid_size),
                           square_colors=((0, 0, 0, 255), (0, 0, 0, 255)),
                           square_outline_colors=((200, 200, 200, 255), (200, 200, 200, 255)))
        grid[0][0]
        
        
class Battle_Screen(pride.gui.gui.Window):
    
    defaults = {"stat_displayer_type" : Stat_Container, "action_menu_type" : Action_Menu,
                "battleground_type" : Battleground, "characters" : tuple()}                
    required_attributes = ("characters", )
    post_initializer = "create_screen_items"
    
    def create_screen_items(self):
        self.create(self.stat_displayer_type, pack_mode="left", characters=self.characters)
        self.create(self.action_menu_type, pack_mode="bottom")
        self.create(self.battleground_type, pack_mode="main", characters=self.characters)
        
    @classmethod
    def unit_test(cls, **kwargs):
        import game2.character as character
        character1 = character.Character(name="Ella!")
        character2 = character.Character(name="Not Ella!")
        return cls(characters=(character1.reference, character2.reference), **kwargs)
        
        
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
            
    defaults = {"h_range" : (0, 40), "current_action" : "move"}
    post_initializer = "create_selections"
    
    def create_selections(self):
        self.create(Move_Button)
        self.create(Attack_Button)
        self.create(Defend_Button)
        self.create(Dodge_Button)
        self.create(Abilities_Button)
        

class Action_Status_Button(pride.gui.gui.Button):
    defaults = {"pack_mode" : "left"}
    required_attributes = ("text", )
    
    def left_click(self, mouse):
        self.parent.current_action = self.text
        
    
class Move_Button(Action_Status_Button):
    
    defaults = {"text" : "move", "pack_mode" : "left"}

        
class Attack_Button(Action_Status_Button):
    
    defaults = {"text" : "attack", "pack_mode" : "left"}
    
    
class Defend_Button(Action_Status_Button):
        
    defaults = {"text" : "defend", "pack_mode" : "left"}
    
    
class Dodge_Button(Action_Status_Button):
        
    defaults = {"text" : "dodge", "pack_mode" : "left"}
    
    
class Abilities_Button(pride.gui.gui.Button):
        
    defaults = {"text" : "abilities", "pack_mode" : "left"}
    
    
class Battleground_Square(pride.gui.gui.Button):
    
    def _get_battleground(self):
        return self.parent.parent.parent
    battleground = property(_get_battleground)
    
    def _get_battle_screen(self):
        return self.parent.parent.parent.parent
    battle_screen = property(_get_battle_screen)
    
    def left_click(self, mouse):            
        self.battleground.action_queue[self.battle_screen.current_character] = ("move", self.reference)
                                            
                
class Action_Queue(dict):
                        
    def __setitem__(self, key, value):
        super(Action_Queue, self).__setitem__(key, value)
        if None not in self.values():
            parent_reference = self["__parent"]
            pride.objects[parent_reference].process_queue()
            characters = self.keys()
            for character in characters:
                self[character] = None
            super(Action_Queue, self).__setitem__("__parent", parent_reference)
            
        
class Battleground(pride.gui.gui.Container):
        
    defaults = {"grid_size" : (5, 5), "characters" : tuple(), "column_button_type" : Battleground_Square}
    mutable_defaults = {"action_queue" : Action_Queue, "character_button" : dict}
    required_attributes = ("characters", )
    post_initializer = "initialize_battleground"
    
    def initialize_battleground(self):
        self.initialize_action_queue()            
        self.create_grid()
     
    def initialize_action_queue(self):
        action_queue = self.action_queue
        action_queue["__parent"] = self.reference
        for character in self.characters:
            action_queue[character] = None
            
    def create_grid(self):
        grid = self.create("pride.gui.grid.Grid", grid_size=(self.grid_size),
                           column_button_type=self.column_button_type,
                           square_colors=((0, 0, 0, 255), (0, 0, 0, 255)),
                           square_outline_colors=((200, 200, 200, 255), (200, 200, 200, 255)))
        self.grid = grid
        
        # todo: add support for more than 2 characters
        character_buttons = self.character_button
        characters = self.characters           
        grid_position = 0
        for character_data in self.characters:
            button = grid[grid_position][grid_position].create(Battleground_Character, character=character_data,
                                                               grid_position=(grid_position, grid_position))            
            grid_position += 1            
            pride.objects[character_data].button = button.reference
            
        self.parent.set_current_character(characters[0])
        
    def process_queue(self):
        action_queue = self.action_queue
        del action_queue["__parent"]
        for character_reference, action in action_queue.items():
            assert action is not None
            getattr(self, "handle_{}".format(action[0]))(character_reference, action[1:])
           
    def handle_move(self, character_reference, destination_reference):
        objects = pride.objects
        character = objects[character_reference]
        character_button = objects[character.button]        
        destination = objects[destination_reference[0]]
        target_x, target_y = destination.grid_position        
        character_x, character_y = character_button.grid_position
        if not (abs(target_x - character_x) > 1 or 
                abs(target_y - character_y) > 1):
            character_button.delete()
            new_button = destination.create(Battleground_Character, character=character_reference,
                                            grid_position=(target_x, target_y))
            character.button = new_button.reference
            new_button.pack()
            
        
class Battleground_Character(pride.gui.gui.Button):
            
    post_initializer = "set_name_text"
    
    def set_name_text(self):
        self.text = pride.objects[self.character].name
        
    def left_click(self, mouse):
        parent = self.parent
        current_character = parent.battle_screen.current_character
        if current_character != self.character:
            parent.action_queue[current_character] = ("attack", self.character)
        
    
class Battle_Screen(pride.gui.gui.Window):
    
    defaults = {"stat_displayer_type" : Stat_Container, "action_menu_type" : Action_Menu,
                "battleground_type" : Battleground, "characters" : tuple(),
                "current_character" : ''}                
    required_attributes = ("characters", )
    post_initializer = "create_screen_items"
    
    def create_screen_items(self):
        characters = self.characters
        self.create(self.stat_displayer_type, pack_mode="left", characters=characters)        
        self.create(self.battleground_type, pack_mode="main", characters=characters)
                
    def set_current_character(self, character_reference):
        self.current_character = character_reference
        
    @classmethod
    def unit_test(cls, **kwargs):
        import game2.character as character
        character1 = character.Character(name="Ella!")
        battle_screen = cls(characters=(character1.reference, ), **kwargs)
        battle_screen._characters = (character1, )
        return battle_screen
        #character2 = character.Character(name="Not Ella!")
        #return cls(characters=(character1.reference, character2.reference), **kwargs)
        
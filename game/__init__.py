import pride.gui.gui
import pride.gui.widgetlibrary

import game.stats

class Stat_Displayer(pride.gui.widgetlibrary.Form):
    
    defaults = {"pack_mode" : "top", "available_points" : 0}
    mutable_defaults = {"entries" : lambda: game.stats.DEFAULT_STATS.copy()}
    
        
class Character_Creation_Dialog(pride.gui.gui.Window):
    
    def __init__(self, **kwargs):
        super(Character_Creation_Dialog, self).__init__(**kwargs)
        container = self.create("pride.gui.gui.Container", pack_mode="top", h_range=(0, 40))
        container.create("pride.gui.widgetlibrary.Text_Box", text="Character Name: ", allow_text_edit=False, 
                                                             pack_mode="left", h_range=(0, 20), w_range=(150, 150))
        container.create("pride.gui.widgetlibrary.Text_Box", text='', allow_text_edit=True, 
                                                             pack_mode="left", h_range=(0, 20))
        container2 = self.create("pride.gui.gui.Container", pack_mode="top")
        container2.create(Stat_Displayer)
                
          
class Start_Screen(pride.gui.gui.Window):
        
    def __init__(self, **kwargs):
        super(Start_Screen, self).__init__(**kwargs)
        self.create("pride.gui.widgetlibrary.Method_Button", text="New Character", 
                    target=self.reference, method="launch_character_creation_dialog",
                    h_range=(0, 20))
                    
    def launch_character_creation_dialog(self):
        dialog = self.create(Character_Creation_Dialog)        
        self.pack()
                
    
class Game_Window(pride.gui.gui.Window):
    
    defaults = {"map_type" : "game.gui.map.Map"}
    
    def __init__(self, **kwargs):
        super(Game_Window, self).__init__(**kwargs)
        self.create(Start_Screen)
        #self.map = self.create(self.map_type)
        
    #def delete(self):
    #    self.map = None
    #    super(Game_Window, self).delete()
        
        
class Game_Application(pride.gui.gui.Application):
                
    defaults = {"application_window_type" : "game.Game_Window"}
    
    
def test_Game_Application():
    import pride.gui
    window = pride.gui.enable()
    pride.objects[window].create(Game_Application)
    
if __name__ == "__main__":
    test_Game_Application()
    
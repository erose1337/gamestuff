# options
# turn based, no timers (synchronous)
#   - a la pokemon
# cooldowns/timers      (asynchronous)
#   - a la diablo
import itertools

import pride.components.base

import game.mechanics.combat
import game.mechanics.droptable

def get_selection(prompt, prompt2, answers):
    """ Displays prompt to the user. Only input from the supplied answers iterable
        will be accepted. . """
    selection = None
    while selection is None:
        selection = raw_input(prompt)
        if selection not in answers:
            print(prompt2)
            selection = None        
    return selection    
              
              
class Handler(object):     
    
    def __init__(self, selection_text=''):        
        super(Handler, self).__init__()
        self.selection_text = selection_text or self.__class__.__name__.split('_')[-2].lower() #  "otherInfo_X_Handler"

        
class Battle_Result_Handler(Handler):
          
    def handle_victory(self, victorious_party, defeated_party):
        victorious_party.alert("Victory!", level=0, display_name=victorious_party.name)
        defeated_party.alert("Defeat!", level=0, display_name=defeated_party.name)
        
    def handle_defeat(self, defeated_party, victorious_party):
        victorious_party.alert("Victory!", level=0, display_name=victorious_party.name)
        defeated_party.alert("Defeat!", level=0, display_name=defeated_party.name)
        
    def handle_draw(self, party1, party2):
        party1.alert("Draw!", level=0, display_name=party1.name)
        party2.alert("Draw!", level=0, display_name=party2.name)
        
    def handle_run(self, fleeing_party, other_party):
        fleeing_party.alert("Runs away!", level=0, display_name=fleeing_party.name)
        
    def handle_surrender(self, surrendering_party, capturer):
        surrendering_party.alert("Surrendered!", level=0, display_name=surrendering_party.name)
        capturer.alert("Now you are my prisoner.", level=0, display_name=capturer.name)
                       
    
class Combat_Handler(Handler):
               
    def handle_attack(self, active_party, other_party):
        raise NotImplementedError()
                
    def handle_defend(self, active_party, other_party):
        raise NotImplementedError()
            
    def handle_ability(self, active_party, other_party):
        raise NotImplementedError()
                
    def handle_item(self, active_party, other_party):
        raise NotImplementedError()
             
    def handle_run(self, active_party, other_party):
        raise NotImplementedError()
         
    def handle_surrender(self, active_party, other_party):        
        raise NotImplementedError()

        
class Synchronous_Combat_Handler(Handler):
        
    verbosity = {"surrender" : 0}
    
    def handle_attack(self, active_party, other_party):
        game.mechanics.combat.process_attack(active_party, other_party)            
        
    def handle_defend(self, active_party, other_party):
        active_party.alert("*Defends*", level=0, display_name=active_party.name)
    
    def handle_ability(self, active_party, other_party):
        active_party.alert("ability: ", level=0, display_name=active_party.name)
        
    def handle_item(self, active_party, other_party):
        active_party.alert("items: ", level=0, display_name=active_party.name)
        
    def handle_run(self, active_party, other_party):
        game.mechanics.combat.process_flee(active_party, other_party)
    
    def handle_surrender(self, active_party, other_party):        
        active_party.alert("surrender!", level=self.verbosity["surrender"],
                           display_name=active_party.name)

                  
class Engine(pride.base.Base):
    
    defaults = {"invalid_selection_prompt" : "Invalid selection",
                "handler_types" : tuple(), "selection_text" : ''}    
    mutable_defaults = {"menu_selection" : list}
    
    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        menu_selection = self.menu_selection
        for handler_type_name in self.handler_types:
            print self, "creating ", handler_type_name
            handler = self.create(handler_type_name)  
            selection_text = handler.selection_text
            setattr(self, selection_text, handler)
            menu_selection.append(selection_text)
        selection_prompt = " ".join("{}" for count in range(len(menu_selection)))                        
        self.selection_prompt = selection_prompt.format(*menu_selection) + "\nChoice: "    
    
        if not self.selection_text:
            self.selection_text = self.__class__.__name__.split('_')[-2].lower() #  "otherInfo_X_Handler"

    def run(self, party1):
        running = True                               
        while running:
            selection = self.present_menu(party1)            
            self.process_selection(selection, party1)                   
        
    def process_selection(self, selection, party):
        return getattr(self, "{}_handler".format(selection))(party)
                
    def present_menu(self, active_party):
        print('*' * 79)        
        #print(self.get_current_status())
        print('*' * 79)
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selection)
        assert selection in self.menu_selection
        return selection
    
    def process_selection(self, selection, party):
        getattr(self, selection).run(party)
                    
    @classmethod
    def unit_test(cls):
        import game.character
        print "Unit testing: ", cls
        engine = cls()        
        party1 = game.character.Character(name="Ella!", npc=False)
        while True:            
            engine.run(party1)  

            
class Hunt_Handler(Engine):
            
    def run(self, *args):
        #raise NotImplementedError()
        party = args[0]
        party.alert("*Hunt*(NotImplemented)", level=0)
        
    
class Gather_Handler(Handler):
        
    class drop_table(game.mechanics.droptable.Drop_Table):
        
        possible_drops = ("game.items.crafting.gather.Short_Stick",
                          "game.items.crafting.gather.Long_Stick",
                          "game.items.crafting.gather.Bluntstone",
                          "game.items.crafting.gather.Sharpstone",
                          "game.items.crafting.gather.Spearstone")       
    
    def run(self, *args):
        party = args[0]
        party.alert("Foraging...", level=0)
        # drop an item
        item_name = self.drop_table.drop_item(1)[0]
        party.alert("Found {}".format(item_name.rsplit('.', 1)[-1]), level=0)
        try:
            party.body.backpack.create(item_name)
        except game.items.backpack.CapacityError:
            party.alert("Item does not fit in storage", level=0)        
        
        
class Chop_Handler(Handler):
    
    def run(self, *args):
        party = args[0]
        party.alert("Chopping wood...", level=0)
        
        
class Mine_Handler(Handler):
    
    def run(self, *args):
        party = args[0]
        party.alert("Mining for ore...", level=0)
        
        
class Fish_Handler(Handler):
            
    def run(self, *args):
        party = args[0]
        party.alert("Fishing...", level=0)
        
        
class Rest_Handler(Handler):
            
    def run(self, *args):
        party = args[0]
        party.alert("Resting...", level=0)
        #party.pass_time() ?
    
    
class Wander_Handler(Engine): 

    defaults = {"handler_types" : ("game.mechanics.enginetest.Hunt_Handler",
                                   "game.mechanics.enginetest.Gather_Handler",
                                   "game.mechanics.enginetest.Chop_Handler", 
                                   "game.mechanics.enginetest.Mine_Handler", 
                                   "game.mechanics.enginetest.Fish_Handler", 
                                   "game.mechanics.enginetest.Rest_Handler")}                      
       
                
class Basic_Game(Engine):
                        
    defaults = {"handler_types" : ("game.mechanics.enginetest.Wander_Handler", )}
    
    
class Synchronous_Combat_Engine(Engine):
    
    menu_selection = ["attack", "defend", "ability", "item", "run", "surrender"]
            
    def run(self, party1, party2):
        battle_engaged = True        
        active_party = party2
        other_party = party1    
        print("\nBeginning battle!...")
        while battle_engaged:
            active_party, other_party = other_party, active_party
            if active_party.is_human_player: 
                last_selection = self.present_menu(active_party, other_party)
            else:
                last_selection = self.combat_ai_handle(active_party, other_party)
            battle_engaged = self.determine_battle_engaged(active_party, other_party, last_selection)
            
        self.end_battle(active_party, other_party, last_selection)
        
    def determine_battle_engaged(self, active_party, other_party, last_selection):        
        continue_flag = True
        if (last_selection in ("run", "surrender") or
            active_party.is_dead or other_party.is_dead):
            continue_flag = False            
        return continue_flag
        
    def determine_battle_outcome(self, active_party, other_party, last_selection):
        if active_party.is_dead:
            if other_party.is_dead:
                outcome = "draw"
            else:
                outcome = "defeat"
        elif other_party.is_dead:
            outcome = "victory"
        else:
            outcome = last_selection
        return outcome
        
    def end_battle(self, party1, party2, last_selection):
        outcome = self.determine_battle_outcome(party1, party2, last_selection)        
        getattr(self.result_handler, "handle_{}".format(outcome))(party1, party2)
                        
    def present_menu(self, active_party, other_party):
        print('*' * 79)        
        print("Currently engaged in combat with: {} (hp: {}/{})".format(other_party.name, *other_party.stats.health.display_values))
        print('*' * 79)
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selection)
        assert selection in self.menu_selection
        getattr(self.synchronous_combat_handler, "handle_{}".format(selection))(active_party, other_party)
        return selection                
    
    def combat_ai_handle(self, active_party, other_party):
        game.mechanics.combat.process_attack(active_party, other_party)
        return "attack"
        
    @classmethod
    def unit_test(cls):
        import game.character
        import game.mechanics.randomgeneration as randomgeneration
        engine = cls()        
        party1 = game.character.Character(name="Ella!", npc=False)
        while True:
            party2 = game.character.Character(name=randomgeneration.random_selection(["Caitlin", "Lacey", "Patti", "Mick"]))
            engine.run(party1, party2)
            party1.stats.health.current_health += 1
                 
                               
class Attack_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        game.mechanics.combat.process_attack(active_party, other_party)
        
        
class Defend_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        active_party.alert("*Defends*(NotImplemented)", level=0, display_name=active_party.name)
        
        
class Ability_Handler(Handler):
           
    def run(self, *args):
        active_party, other_party = args
        active_party.alert("*Ability*(NotImplemented)", level=0, display_name=active_party.name)
        
        
class Item_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        active_party.alert("*Items*(NotImplemented)", level=0, display_name=active_party.name)
        
        
class Run_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        game.mechanics.combat.process_flee(active_party, other_party)
        
        
class Surrender_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        active_party.alert("surrender!", level=0, display_name=active_party.name)
        other_party.alert("You are now my prisoner.", level=0, display_name=active_party.name)
        
if __name__ == "__main__":
    #Engine.unit_test()
    Basic_Game.unit_test()
    #Synchronous_Combat_Engine.unit_test()
    
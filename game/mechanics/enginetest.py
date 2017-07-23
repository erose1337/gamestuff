# options
# turn based, no timers (synchronous)
#   - a la pokemon
# cooldowns/timers      (asynchronous)
#   - a la diablo
import itertools

import game.mechanics.combat

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
              
              
class Battle_Result_Handler(object):
          
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
                       
    
class Combat_Handler(object):
               
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

        
class Synchronous_Combat_Handler(object):
        
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

                           
class Synchronous_Combat_Engine(object):
    
    menu_selections = ["attack", "defend", "ability", "item", "run", "surrender"]
    selection_prompt = " ".join("{}" for count in range(len(menu_selections)))        
    selection_prompt = selection_prompt.format(*menu_selections) + "\nChoice: "    
    invalid_selection_prompt = "Invalid selection"
            
    result_handler = Battle_Result_Handler()
    combat_handler = Synchronous_Combat_Handler()
    
    def __init__(self, *args, **kwargs):
        super(Synchronous_Combat_Engine, self).__init__(*args, **kwargs)
        
        
    def begin_battle(self, party1, party2):
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
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selections)
        assert selection in self.menu_selections
        getattr(self.combat_handler, "handle_{}".format(selection))(active_party, other_party)
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
            engine.begin_battle(party1, party2)
            party1.stats.health.current_health += 1
            
if __name__ == "__main__":
    Synchronous_Combat_Engine.unit_test()
    
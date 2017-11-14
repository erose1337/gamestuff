import itertools
import pprint
import os

import pride.components.base

import game.character2
import game.mechanics.combat2
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

        
class Return_Handler(Handler):
            
    def run(self, *args):
        self.parent.running = False
        
        
class Battle_Result_Handler(Handler):
          
    def handle_victory(self, victorious_party, defeated_party):
        victorious_party.alert("Victory!", level=0, display_name=victorious_party.name)
        defeated_party.alert("Defeat!", level=0, display_name=defeated_party.name)
        victorious_party.alert("Gained {} experience".format(10 ** defeated_party.skills.combat.level))                        
        victorious_party.xp += 10 ** defeated_party.skills.combat.level
        
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
        game.mechanics.combat2.process_attack(active_party, other_party)            
        
    def handle_defend(self, active_party, other_party):
        active_party.alert("*Defends*", level=0, display_name=active_party.name)
    
    def handle_ability(self, active_party, other_party):
        active_party.alert("ability: ", level=0, display_name=active_party.name)
        
    def handle_item(self, active_party, other_party):
        active_party.alert("items: ", level=0, display_name=active_party.name)
        
    def handle_run(self, active_party, other_party):
        game.mechanics.combat2.process_flee(active_party, other_party)
    
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
            handler = self.create(handler_type_name)  
            selection_text = handler.selection_text
            setattr(self, selection_text, handler)
            menu_selection.append(selection_text)            
        menu_selection.append("exit")
        
        selection_prompt = " ".join("{}" for count in range(len(menu_selection)))                        
        self.selection_prompt = selection_prompt.format(*menu_selection) + "\nChoice: "    
    
        if not self.selection_text:
            self.selection_text = self.__class__.__name__.split('_')[-2].lower() #  "otherInfo_X_Handler"

    def run(self, party1):
        self.running = True                               
        while self.running:
            selection = self.present_menu(party1)   
            if selection == "exit":
                break
            self.process_selection(selection, party1)                   
        
    def process_selection(self, selection, party):
        return getattr(self, "{}_handler".format(selection))(party)
                
    def present_menu(self, active_party):
        print('*' * 79)                
        print('*' * 79)
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selection)
        assert selection in self.menu_selection
        return selection
    
    def process_selection(self, selection, party):
        getattr(self, selection).run(party)
                   
    def return_handler(self, party):
        self.running = False
        
    @classmethod
    def unit_test(cls):
        import game.character2
        print "Unit testing: ", cls
        engine = cls()        
        skills = game.character2.Skills(health=1, dot=1, regen=1, soak=1, critical_hit=1, damage=10)
        skills.combat.attack.attack_focus = "critical hit"
        skills.combat.defense.defense_focus = "regen"
        party1 = game.character2.Character(name="Ella!", npc=False, skills=skills)        
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
        item = resolve_string(item_name)()
        try:
            party.body.backpack.add(item)
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
       
    
class StartMenu_Handler(Engine):
        
    defaults = {"handler_types" : ("game.mechanics.enginetest.CharacterCreation_Handler",
                                   "game.mechanics.enginetest.LoadCharacter_Handler")}
                                   
                                   
class CharacterCreation_Handler(Handler):
                                
    def __init__(self, selection_text="Create character"):
        super(CharacterCreation_Handler, self).__init__(selection_text)
    
    @staticmethod
    def run(*args):        
        while True:
            name = raw_input("Name: ")
            prompt = "Select an attack focus: {} or {} or {}: "
            selections = ("critical hit", "dot", "strength")
            attack_focus = get_selection(prompt.format(*selections), "invalid selection", selections)
            
            prompt = "Select a defense focus: {} or {} or {}: "
            selections = ("dodge", "regen", "soak")
            defense_focus = get_selection(prompt.format(*selections), "invalid selection", selections)
            
            skills = game.character2.Skills(damage=10)
            skills.combat.attack.attack_focus = attack_focus
            skills.combat.defense.defense_focus = defense_focus
            character = game.character2.Character(name=name, npc=False, skills=skills)
            
            Character_Handler.run(character)
            if 'y' == raw_input("Use this character?: y/n ").lower():
                break
                
        with open("{}.sav".format(name), "wb") as _file:
            _file.truncate()
            _file.write(character.save())
            
            
class LoadCharacter_Handler(Handler):
                
    def __init__(self, selection_text="Load character"):
        super(LoadCharacter_Handler, self).__init__(selection_text)
        
    @staticmethod
    def run(*args):        
        name = raw_input("Enter character name: ")
        if os.path.lexists(name + ".sav"):
            with open("{}.sav".format(name), "rb") as _file:
                data = _file.read()            
            character = game.character2.Character.load(data)
            engine = Basic_Game()
            engine.run(character)
            with open("{}.sav".format(name), "wb") as _file:
                _file.truncate()
                _file.write(character.save())
        else:
            print "Character {} does not exist".format(name)
                
            
class Basic_Game(Engine):
                        
    defaults = {"handler_types" : ("game.mechanics.enginetest.Character_Handler",
                                   "game.mechanics.enginetest.Town_Handler",
                                   "game.mechanics.enginetest.Wander_Handler", 
                                   "game.mechanics.enginetest.Crafting_Handler")}
    

class Town_Handler(Engine):
        
    defaults = {"handler_types" : ("game.mechanics.enginetest.Duel_Handler", )}
    
    def run(self, party):
        party.health = party.max_health
        super(Town_Handler, self).run(party)
        
    
class Duel_Handler(Engine):
    
    defaults = {"handler_types" : ("game.mechanics.enginetest.FairFight_Handler", )}
    
    
class FairFight_Handler(Handler):
        
    def __init__(self, selection_name="Fair fight"):
        super(FairFight_Handler, self).__init__(selection_name)
    
    def run(self, player):
        level = player.skills.combat.level
        opponent_skill = game.character2.Skills.random_skills(level)
        opponent = game.character2.Character(name="captive beast", skills=opponent_skill)
        battle = Synchronous_Combat_Engine()
        battle.run(player, opponent)
        
    
class Character_Handler(Handler):
     
    @staticmethod
    def run(*args):
        party = args[0]                
        string = "Name: {}  Combat: level: {}   xp: {}  damage: {}   hp:    {}/{}\n"
        string += "critical hit:  {}    DoT:    {}   strength: {}   focus: {}\n"
        string += "dodge:         {}    regen:  {}   soak:     {}   focus: {}\n"
        skills = party.skills.combat
        attack = skills.attack
        defense = skills.defense             
        print string.format(party.name, skills.level, party.xp, skills.damage, party.health, party.max_health,
                            attack.critical_hit.level, attack.dot.level, attack.strength.level, attack.attack_focus,
                            defense.dodge.level, defense.regen.level, defense.soak.level, defense.defense_focus)
                               
        
class Crafting_Handler(Engine):
        
    defaults = {"handler_types" : ("game.mechanics.enginetest.Tools_Handler", )}
    
    
class Tools_Handler(Handler):   

    recipes = ("game.items.crafting.gather.Hammer_Handle",
               "game.items.crafting.gather.Hammer_Head")
    recipe_info = dict((name.rsplit('.', 1)[-1], name) for name in recipes)   
    recipe_names = recipe_info.keys()
        
    def run(self, *args):
        party = args[0]        
        party.body.backpack.display_contents()        
        selection = get_selection("Available recipes:\n{}\nChoice: ".format(pprint.pformat(self.recipe_names)), "invalid selection", self.recipe_names)       
        party.alert("Crafting {}...".format(selection), level=0)
        # resolve selection to item_type
        item_type = self.recipe_info[selection]                
        # resolve item_type to item
        item_class = resolve_string(item_type)
        
        # find required components for item in backpack
        backpack_storage = party.body.backpack._storage
        components = dict()
        for slot in item_class.component_pieces:
            for item in backpack_storage:
                if slot in item.occupied_slots:
                    components[slot] = item
                    backpack_storage.remove(item)
                    print "Found required component: ", slot, item
                    break
        
        # find required tools for item in backpack        
        for tool_type in item_class.required_tools_to_assemble:
            print tool_type
            for item in backpack_storage:                
                try:
                    if item.tool_type == tool_type:                
                        components[tool_type] = item                        
                        break
                except AttributeError:
                    continue                    
            else:
                party.alert("Missing required tool: {}".format(tool_type), level=0)
                
        # assemble item and insert into backpack
        print "Building with components: ", components
        try:
            item = item_class.assemble(**components)
        except game.items.GenericGameActionFailure as exception:
            party.alert(exception.message, level=0)        
        else:
            party.body.backpack.add(item)
        
        
class Synchronous_Combat_Engine(Engine):
    
    defaults = {"handler_types" : ("game.mechanics.enginetest.Attack_Handler", 
                                   "game.mechanics.enginetest.Defend_Handler", 
                                   "game.mechanics.enginetest.Ability_Handler", 
                                   "game.mechanics.enginetest.Item_Handler", 
                                   "game.mechanics.enginetest.Flee_Handler", 
                                   "game.mechanics.enginetest.Surrender_Handler")}
    
    def __init__(self, *args, **kwargs):
        super(Synchronous_Combat_Engine, self).__init__(*args, **kwargs)
        self.battle_result_handler = Battle_Result_Handler()
        
    def run(self, party1, party2):
        if party1.is_dead or party2.is_dead:
            raise ValueError("Battle initiated with dead participants:\nparty1.is_dead: {};\nparty2.is_dead: {}".format(party1.is_dead, party2.is_dead))
        battle_engaged = True        
        active_party = party2
        other_party = party1    
        print("\nBeginning battle!...")
        while battle_engaged:
            active_party, other_party = other_party, active_party
            if not active_party.npc: 
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
        getattr(self.battle_result_handler, "handle_{}".format(outcome))(party1, party2)
                        
    def present_menu(self, active_party, other_party):
        print('*' * 79)      
        print("Current stats: hp: {}".format(active_party.health))
        print("Currently engaged in combat with: {} (hp: {})".format(other_party.name, other_party.health))
        print('*' * 79)
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selection)
        assert selection in self.menu_selection
        getattr(self, selection).run(active_party, other_party)
        return selection                
    
    def combat_ai_handle(self, active_party, other_party):
        game.mechanics.combat2.process_attack(active_party, other_party)
        return "attack"
        
    @classmethod
    def unit_test(cls):
        import game.character2
        import game.mechanics.randomgeneration as randomgeneration
        engine = cls()        
        skills = game.character2.Skills(health=1, dot=1, regen=1, soak=1, critical_hit=1, damage=10)
        skills.combat.attack.attack_focus = "critical hit"
        skills.combat.defense.defense_focus = "regen"
        party1 = game.character2.Character(name="Ella!", npc=False, skills=skills)
        assert party1.skills.combat.attack is skills.combat.attack
        assert hasattr(party1.skills.combat.attack.attack_focus)
        while True:
            party2 = game.character2.Character(name=randomgeneration.random_selection(["Caitlin", "Lacey", "Patti", "Mick"]))
            engine.run(party1, party2)
                             
                               
class Attack_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        game.mechanics.combat2.process_attack(active_party, other_party)
        
        
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
        
        
class Flee_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        game.mechanics.combat2.process_flee(active_party, other_party)
        
        
class Surrender_Handler(Handler):
            
    def run(self, *args):
        active_party, other_party = args
        active_party.alert("surrender!", level=0, display_name=active_party.name)
        other_party.alert("You are now my prisoner.", level=0, display_name=active_party.name)
        
if __name__ == "__main__":
    #Engine.unit_test()
    #Basic_Game.unit_test()
    #Synchronous_Combat_Engine.unit_test()
    menu = StartMenu_Handler()
    menu.run(None)
    
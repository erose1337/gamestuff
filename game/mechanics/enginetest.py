import traceback
import pprint
import os
import random

import pride.components.base

import game.character2
import game.mechanics.combat2
import game.mechanics.droptable

ELEMENT_BONUS = {"Fire" : "Air", "Air" : "Stone", "Stone" : "Electric", 
                 "Electric" : "Water", "Water" : "Fire", "Excellence" : "None", "Neutral" : "None"}
ELEMENT_PENALTY = dict((value, key) for key, value in ELEMENT_BONUS.items())
del ELEMENT_PENALTY["None"]
ELEMENT_PENALTY["Excellence"] = "None"
ELEMENT_PENALTY["Neutral"] = "None"

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
              
              
class Handler(pride.base.Base):     
    
    defaults = {"selection_text" : ''}
    
    def __init__(self, *args, **kwargs):        
        super(Handler, self).__init__(*args, **kwargs)
        if self.selection_text == '':
            self.selection_text = self.__class__.__name__.split('_')[-2].lower() #  "otherInfo_X_Handler"

        
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
        
    def handle_flee(self, fleeing_party, other_party):
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
                "handler_types" : tuple(), "selection_text" : '',
                "menu_includes_exit" : True}   
                
    mutable_defaults = {"menu_selection" : list}
    
    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        menu_selection = self.menu_selection
        for handler_type_name in self.handler_types:            
            handler = self.create(handler_type_name)  
            selection_text = handler.selection_text
            setattr(self, selection_text, handler)
            menu_selection.append(selection_text)            
        if self.menu_includes_exit:
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
            
    defaults = {"selection_text" : "Create character", 
                "element_prompt" : "You may choose to be empowered with a certain element.\nDoing so will bestow an advantage against another opposing element, as well as a weakness against another. \nAlternatively, you may choose to remain neutral and create a mundane but exceptional mortal.",
                "element_selections" : ("Fire", "Air", "Stone", "Electric", "Water", "Excellence"),
                "element_descriptions" : ("Fire:\n    You are empowered with fire.\n    +50% to Air, -50% to Water",
                                          "\nAir:\n    You are empowered with air.\n    +50% to Stone, -50% to Fire",
                                          "\nStone:\n    You are empowered with Stone.\n    +50% to Electric, -50% to Air",
                                          "\nElectric:\n    You are empowered with Electricity.\n    +50% to Water, -50% to Stone",
                                          "\nWater:\n    You are empowered with Water.\n    +50% to Fire, -50% to Electric",
                                          "\nExcellence:\n    You are a normal mortal with exceptional skills.\n    No damage bonus or resistance"),
                "critical_hit_description" : "Provides a 15% chance to deal 6.6 * level extra damage",
                "dot_description" : "Provides a 33% chance to deal 3.3 * level extra damage",
                "strength_description" : "Increases minimum damage by 1 * level",
                "dodge_description" : "Provides a 15% chance to avoid 6.6 * level damage",
                "regen_description" : "Provides a 33% chance to recover 3.3 * level health each turn",
                "soak_description" : "Reduces incoming damage by 1 point per level"}
    
    def run(self, *args):        
        while True:
            name = raw_input("Name: ")
            print self.element_prompt
            print ''.join(self.element_descriptions)
            element = get_selection("Please choose an element: ", "invalid selection", self.element_selections)            
            
            prompt = "Select an attack focus:\n{}:\n   {}\n{}:\n   {}\n{}:\n   {}\nSelection: "
            selections = ("critical hit", self.critical_hit_description, 
                          "dot", self.dot_description,
                          "strength", self.strength_description)
            attack_focus = get_selection(prompt.format(*selections), "invalid selection", selections).replace(' ', '_')
            
            prompt = "Select a defense focus:\n{}:\n   {}\n{}:\n   {}\n{}:\n   {}\nSelection: "
            selections = ("dodge", self.dodge_description,
                          "regen", self.regen_description, 
                          "soak", self.soak_description)
            defense_focus = get_selection(prompt.format(*selections), "invalid selection", selections).replace(' ', '_')
            
            skills = game.character2.Skills(damage=10)
            skills.combat.attack.attack_focus = attack_focus
            skills.combat.defense.defense_focus = defense_focus
            character = game.character2.Character(name=name, npc=False, skills=skills, element=element)
            
            Character_Handler.run(character)
            if 'y' == raw_input("Use this character?: y/n ").lower():
                break
                
        with open("{}.sav".format(name), "wb") as _file:
            _file.truncate()
            _file.write(character.save())
            
            
class LoadCharacter_Handler(Handler):
                
    defaults = {"selection_text" : "Load character"}

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
                                   "game.mechanics.enginetest.Quests_Handler",
                                   "game.mechanics.enginetest.Town_Handler",
                                   "game.mechanics.enginetest.Wander_Handler", 
                                   "game.mechanics.enginetest.Crafting_Handler")}
    

class Quests_Handler(Engine):
        
    defaults = {"handler_types" : ("game.mechanics.enginetest.The_Duel_Quest_Handler", )}
    

class Quest_Handler(Handler):
        
    defaults = {"quest_name" : '', "quest_description" : '',
                "quest_starting_point" : '', "quest_reward" : '',
                "recommended_level" : 0}
                
    def __init__(self, *args, **kwargs):            
        super(Quest_Handler, self).__init__(*args, **kwargs)
        self.selection_text = self.quest_name
                    
    def run(self, player):
        print("\nQuest:     {}      recommended level: {}".format(self.quest_name, self.recommended_level))
        print("Completed:   {}".format(self.quest_name in player.complete_quests))
        print("Description:\n   {}".format(self.quest_description))
        print("Starting point:  {}".format(self.quest_starting_point))
        print("Reward:  {}".format(self.quest_reward_hint))
    
    
class The_Duel_Quest_Handler(Quest_Handler):
    
    defaults = {"quest_name" : "The Duel", "quest_description" : "Test your mettle at the duel arena!",
                "quest_starting_point" : "town->duel", "quest_reward_hint" : "Combat XP",
                "recommended_level" : 0}
                    
        
class Town_Handler(Engine):
        
    defaults = {"handler_types" : ("game.mechanics.enginetest.Duel_Handler", )}
    
    def run(self, party):
        party.health = party.max_health
        super(Town_Handler, self).run(party)
        
    
class Duel_Handler(Engine):
    
    defaults = {"handler_types" : ("game.mechanics.enginetest.FairFight_Handler", 
                                   "game.mechanics.enginetest.The_Duel_Handler")}
    

class The_Duel_Handler(Handler):
       
    defaults = {"selection_text" : "The Duel"}
    
    def run(self, player):
        assert hasattr(player.skills.combat.attack, "attack_focus")
        opponent_skill = game.character2.Skills.random_skills(0)                
        opponent = game.character2.Character(name="El toriablo", skills=opponent_skill)
        opponent.health -= 25
        battle = Synchronous_Combat_Engine()
        outcome = battle.run(player, opponent)
        if outcome == "victory" and "The Duel" not in player.complete_quests and not player.is_dead:
            assert hasattr(player.skills.combat.attack, "attack_focus")
            player.xp += 90
            player.complete_quests.add("The Duel")
    
    
class FairFight_Handler(Handler):
        
    defaults = {"selection_text" : "Fair fight"}

    def run(self, player):
        level = player.skills.combat.level        
        opponent_skill = game.character2.Skills.random_skills(level)
        element = random.choice(ELEMENT_BONUS.keys())
        if element == "Excellence":
            element = "Neutral"
        element = "Water"
        opponent = game.character2.Character(name="captive beast", skills=opponent_skill, element=element)
        battle = Synchronous_Combat_Engine()
        battle.run(player, opponent)
        
    
class Character_Handler(Handler):
     
    @staticmethod
    def run(*args):
        party = args[0]                
        string = "Name: {}  level: {}   xp:     {}   damage:   {}   hp:    {}/{}\n"
        
        element = party.element
        bonus = ELEMENT_BONUS[element]
        penalty = ELEMENT_PENALTY[element]
        string += "Element: {}  +50% against: {}   -50% against {}\n".format(element, bonus, penalty)
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
                                   "game.mechanics.enginetest.Surrender_Handler"),
                "menu_includes_exit" : False}
    mutable_defaults = {"battle_result_handler" : Battle_Result_Handler}
                    
    def run(self, party1, party2):
        if party1.is_dead or party2.is_dead:
            raise ValueError("Battle initiated with dead participants:\nparty1.is_dead: {};\nparty2.is_dead: {}".format(party1.is_dead, party2.is_dead))
        battle_engaged1 = battle_engaged2 = True        
        active_party = party1
        other_party = party2        
        print("\nBeginning battle!...")
        while battle_engaged1 and battle_engaged2:
            # active_party, other_party = other_party, active_party 
            selection1, flag1 = self.handle_turn(active_party, other_party)
            selection2, flag2 = self.handle_turn(other_party, active_party)
                               
            battle_engaged1 = self.determine_battle_engaged(active_party, other_party, selection1)
            battle_engaged2 = self.determine_battle_engaged(other_party, active_party, selection2)
        return self.end_battle(active_party, other_party, selection1)
        
    def handle_turn(self, active_party, other_party):
        if not active_party.npc: 
            handler = self.present_menu
        else:
            handler = self.combat_ai_handle
        return handler(active_party, other_party)
        
    def determine_battle_engaged(self, active_party, other_party, last_selection):        
        continue_flag = True
        if (last_selection in ("flee", "surrender") or
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
        return outcome
        
    def present_menu(self, active_party, other_party):
        print('*' * 79)      
        print("Current stats: hp: {}".format(active_party.health))
        print("Currently engaged in combat with: {} (hp: {})".format(other_party.name, other_party.health))
        print('*' * 79)
        selection = get_selection(self.selection_prompt, self.invalid_selection_prompt, self.menu_selection)
        assert selection in self.menu_selection
        flag = getattr(self, selection).run(active_party, other_party)
        return selection, flag
    
    def combat_ai_handle(self, active_party, other_party):
        game.mechanics.combat2.process_attack(active_party, other_party)
        return "attack", True
        
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
        if game.mechanics.combat2.process_flee(active_party, other_party):
            end_battle = True
            return end_battle
        
        
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
    
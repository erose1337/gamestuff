# balance testing program
# performs lots of battles between combatants with a random distribution of skills
# if a certain skill wins more often then others, it is possibly over-powered
import pprint

import game.mechanics.enginetest
import game.mechanics.combat2
import game.character2

class Balance_Test(object):
    
    @classmethod
    def unit_test(cls, trials=100):
        battle = game.mechanics.enginetest.Synchronous_Combat_Engine()
        verbosity = dict((item, 'v') for item in game.character2.Character.verbosity.keys())
        for level in range(10, 11):
            characters = []            
            for skill in ("critical_hit", "dot", "strength", "dodge", "regen", "soak"): 
                kwargs = {skill : level}
                skills = game.character2.Skills(**kwargs)
                kwargs = {"skills" : skills, "name" : skill, "verbosity" : verbosity}
                characters.append(game.character2.Character(**kwargs))
                
            battle_log = {}            
            for trial in range(trials):
              #  print("Trial {}/{}".format(trial, trials))
                for character in characters:
                    for character2 in characters:
                        if character is character2:
                            continue
                        character.health = character.max_health
                        character2.health = character2.max_health
                        while not (character.is_dead or character2.is_dead):
                            game.mechanics.combat2.process_attack(character, character2)
                            game.mechanics.combat2.process_attack(character2, character)
                        if character.is_dead:
                            if not character2.is_dead:
                                try:
                                    battle_log[(character.name, character2.name)] -= 1
                                except KeyError:
                                    battle_log[(character.name, character2.name)] = -1
                        elif character2.is_dead:
                            try:
                                battle_log[(character.name, character2.name)] += 1
                            except KeyError:
                                battle_log[(character.name, character2.name)] = 1
            pprint.pprint(battle_log)
            
if __name__ == "__main__":
    Balance_Test.unit_test()
    
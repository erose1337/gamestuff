# balance testing program
# performs lots of battles between combatants with a random distribution of skills
# if a certain skill wins more often then others, it is possibly over-powered
import pprint

import game.mechanics.enginetest
import game.mechanics.combat2
import game.character2

class Balance_Test(object):
    
    @classmethod
    def unit_test(cls, trials=50, test_skills=("critical_hit", "dot", "strength", "dodge", "regen", "soak")):
        battle = game.mechanics.enginetest.Synchronous_Combat_Engine()
        verbosity = dict((item, 'v') for item in game.character2.Character.verbosity.keys())
        for level in range(10, 11):
            characters = []            
            for skill in test_skills:
                kwargs = {skill : level, "health" : 100 + (10 * level), "damage" : 10 + level}
                skills = game.character2.Skills(**kwargs)
                kwargs = {"skills" : skills, "name" : skill, "verbosity" : verbosity}
                characters.append(game.character2.Character(**kwargs))
                
            battle_log = {}            
            for trial in range(trials):
                #print("Trial {}/{}".format(trial, trials))
                for character in characters:
                    for character2 in characters:
                        if character is character2:
                            continue
                        character.health = character.max_health
                        character2.health = character2.max_health
                        
                        #verbosity = dict((item, 0) for item in game.character2.Character.verbosity.keys())
                        #character2.verbosity = character.verbosity = verbosity
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
    
def test_probability():
    import random
    chance1 = 10
    damage1 = 5
    
    chance2 = 33    
    damage2 = 2
    
    samples1 = []
    samples2 = []
    crits_dodged = []
    for count in range(1000):
        if random.randint(0, 100) <= chance1:
            samples1.append(random.randint(1, damage1))
            if random.randint(0, 100) <= chance2:
                crits_dodged.append(random.randint(1, damage2))
        if random.randint(0, 100) <= chance2:
            samples2.append(random.randint(1, damage2))
    print len(samples1), sum(samples1)
    print len(samples2), sum(samples2)
    print(float(len(crits_dodged)) / len(samples1), sum(crits_dodged))
        
if __name__ == "__main__":
    #trials = 50
    #test_skills = ["critical_hit", "strength", "dodge", "soak"]          
    #for test_skill in ("critical_hit", "dodge", "soak", "strength"):#test_skills:
    #    print "Testing: {}".format(test_skill)
    #    _test_skills = test_skills[:]
    #    _test_skills.remove(test_skill)
    #    for skill in _test_skills:
    #        Balance_Test.unit_test(trials=trials, test_skills=(test_skill, skill))
    test_probability()
    
    
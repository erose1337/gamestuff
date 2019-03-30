import itertools
import operator

import pride.components.base

import effects

class Battle(pride.components.base.Base):

    defaults = {"characters" : tuple()}
    required_attributes = ("characters", )

    def engage(self):
        characters = self.characters
        while True:
            for character in characters:
                print character.format_stats()
                print
            self.process_actions(characters)
            self.process_effects(characters)
            if self.determine_battle_over(characters):
                break
            yield
        outcome = self.determine_outcome(characters)
        if outcome == "draw":
            print("Draw!")
        else:
            print("Winner: {}".format(outcome[0].name))

    def process_actions(self, characters):
        queue = []
        for character in characters:
            queue.append(character.select_action(characters))
        for action in sorted(queue, key=operator.attrgetter("priority")):
            action.evaluate()

    def process_effects(self, characters):
        # copy queue because apply can remove elements from queue during iteration
        #print("Evaluating first queue")
        gen = (character.effect_queue[effects.STANDARD_QUEUE][:] for character in characters)
        for effect, source, target in itertools.chain(*gen):
            assert not isinstance(effect, effects.Damage), effect
            effect.apply(source, target)
        #print("Evaluating damage queue...")
        gen = (character.effect_queue[effects.DAMAGE_QUEUE][:] for character in characters)
        for effect, source, target in itertools.chain(*gen):
            assert isinstance(effect, effects.Damage), effect
            effect.apply(source, target)
        #print("Evaluating post queue...")
        gen = (character.effect_queue[effects.POST_QUEUE][:] for character in characters)
        for effect, source, target in itertools.chain(*gen):
            effect.apply(source, target)

    def determine_battle_over(self, characters):
        living_characters = [character for character in characters if not character.is_dead]
        if len(living_characters) <= 1:
            return True

    def determine_outcome(self, characters):
        living_characters = [character for character in characters if not character.is_dead]
        if len(living_characters) == 0:
            return "draw"
        else:
            assert len(living_characters) == 1
            return living_characters

def test_battle():
    import character
    player1 = character.Character.from_sheet("demochar.cef")
    player2 = character.Character.from_sheet("demochar2.cef")
    battle = Battle(characters=(player1, player2))
    engagement = battle.engage()
    for round in engagement:
        pass

if __name__ == "__main__":
    test_battle()

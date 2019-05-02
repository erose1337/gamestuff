import itertools
import operator

import pride.components.base

#   - battles
#   - collect resources
#      - collect items
#      - build something
#   - obtain equipment
#   - visit destination
#      - interact with other characters
#   - learn about/enable a new quest

class Outcome(pride.components.base.Base):

    defaults = {"result" : None}

    def evaluate(self):
        print self.result


class Event(pride.components.base.Base):

    defaults = {"characters" : tuple(), "effect_queue_count" : 0}
    required_attributes = ("characters", )

    def engage(self):
        characters = self.characters
        display_state = self.display_state
        get_actions = self.get_actions
        process_actions = self.process_actions
        process_effects = self.process_effects
        determine_outcome = self.determine_outcome
        while True:
            yield display_state()
            actions = get_actions()
            process_actions(actions)
            process_effects()
            outcome, yield_flag = determine_outcome()
            yield outcome, yield_flag

    def display_state(self):
        raise NotImplementedError()

    def get_actions(self):
        raise NotImplementedError()

    def process_actions(self, actions):
        for action in sorted(actions, key=operator.attrgetter("priority")):
            action.evaluate()

    def process_effects(self):
        # copy queue because apply can remove elements from queue during iteration
        characters = self.characters
        for queue_number in range(self.effect_queue_count):
            gen = (character.effect_queue[queue_number][:] for character in characters)
            for effect, source, target in itertools.chain(*gen):
                effect.apply(source, target)

    def determine_outcome(self):
        raise NotImplementedError()


class Battle(Event):

    defaults = {"effect_queue_count" : 3}
    mutable_defaults = {"action_queue" : list}

    def display_state(self):
        return (_character.format_stats() for _character in self.characters)

    def add_action(self, action):
        self.action_queue.append(action)
        if len(self.action_queue) == len(self.characters):
            pass
            # do stuff

    def get_actions(self):
        return self.action_queue

    def determine_outcome(self):
        living_characters = [character for character in self.characters if not character.is_dead]
        length = len(living_characters)
        if length == 0:
            return ("draw", None), True
        elif length == 1:
            return ("win", living_characters[0]), True
        else:
            return ("ongoing", living_characters), False


class Event_Processor(pride.components.base.Base):

    def __init__(self, event, **kwargs):
        super(Event_Processor, self).__init__(**kwargs)
        self.engagement = event.engage()

    def evaluate(self):
        engagement = self.engagement
        display = self.display
        while True:
            display_info = next(engagement)
            display(display_info)

            result, concluded_flag = next(engagement)
            if concluded_flag:
                return Outcome(result=result)

    def display(self, display_info):
        for line in display_info:
            print line
            print

def test_battle():
    import character
    player1 = character.Character.from_sheet("demochar.cef")
    player2 = character.Character.from_sheet("demochar2.cef")
    battle_event = Battle(characters=(player1, player2))
    processor = Event_Processor(battle_event)
    outcome = processor.evaluate()
    outcome.evaluate()
    raise SystemExit()

if __name__ == "__main__":
    test_battle()

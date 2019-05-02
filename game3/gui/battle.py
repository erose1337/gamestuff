import pride.gui.gui
import pride.gui.grid


import game3.events
import game3.actions


class Battle_Event(game3.events.Battle):

    mutable_defaults = {"actions" : list}

    def __init__(self, **kwargs):
        super(Battle_Event, self).__init__(**kwargs)
        self.thread = self.engage()

    def run(self):
        return next(self.thread)

    def engage(self):
        characters = self.characters
        display_state = self.display_state
        get_actions = self.get_actions
        process_actions = self.process_actions
        process_effects = self.process_effects
        determine_outcome = self.determine_outcome
        actions = self.actions
        while True:
            yield display_state()
            while True:
                if self.get_actions():
                    process_actions(actions)
                    del actions[:]
                    process_effects()
                    outcome, yield_flag = determine_outcome()
                    yield outcome, yield_flag
                    break
                else:
                    yield "waiting", False

    def add_action(self, action):
        self.actions.append(action)

    def get_actions(self):
        if len(self.actions) == len(self.characters):
            return True


class Battle_Processor(game3.events.Event_Processor):

    def __init__(self, **kwargs):
        super(Battle_Processor, self).__init__(**kwargs)
        self.thread = self.evaluate()

    def run(self):
        return next(self.thread)

    def evaluate(self):
        engagement = self.engagement
        display = self.display
        while True:
            display_info = next(engagement)
            display(display_info)

            result, concluded_flag = next(engagement)
            if concluded_flag:
                yield Outcome(result=result)
            else:
                yield None

    def display(self, display_info):
        pride.objects[self.parent.actions_menu.status_window].add_text('\n'.join(display_info))


class Status_Box(pride.gui.gui.Container):

    defaults = {"pack_mode" : "bottom"}

    def add_text(self, text):
        self.text += '\n' + text


class Grid_Square(pride.gui.gui.Button):

    def left_click(self, mouse):
        self.parent_application.select_cell(self.grid_position)

    def add_characters(self, *args):
        self._characters.extend(args)

    def remove_characters(self, *args):
        _characters = self._characters
        for character in args:
            _characters.remove(character)


class Team(pride.gui.gui.Container):

    mutable_defaults = {"characters" : list}

    def add_character(self, character):
        self.characters.append(self.create(Character, character=character,
                                           text=character.name).reference)


class Character(pride.gui.gui.Button):

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)

    def left_click(self, mouse):
        self.parent_application.select_target(self)


# need to make action/ability selection menus
class Ability_Button(pride.gui.gui.Button):

    def left_click(self, mouse):
        self.alert("Click")


class Ability_Selector(pride.gui.widgetlibrary.Page_Switching_Window):

    defaults = {"character" : None}
    required_attributes = ("character", )

    def __init__(self, **kwargs):
        super(Ability_Selector, self).__init__(**kwargs)
        abilities = self.character.abilities
        for tree_name in abilities:
            tree = getattr(abilities, tree_name)
            page = self.create("pride.gui.gui.Container", h_range=(0, .20))
            page.create("pride.gui.gui.Container", text=tree_name, pack_mode="top")
            for ability_name in tree:
                page.create(Ability_Button, text=ability_name)
            self.pages.append(page)
        self.initialize_pages()


class Grid_Cell(pride.gui.gui.Container):

    def __init__(self, **kwargs):
        super(Grid_Cell, self).__init__(**kwargs)
        #display = self.create("pride.gui.gui.Container", text=str(self.grid_position),
        #                      pack_mode="bottom", h_range=(0, .05))
        self.tip_bar_text = str(self.grid_position)

    def left_click(self, mouse):
        self.parent_application.select_target_place(self.grid_position)


class Battle_Grid(pride.gui.grid.Grid):

    defaults = {"grid_size" : (4, 4), "pack_mode" : "left",
                "column_button_type" : Grid_Cell}


class Character_Icon(pride.gui.gui.Button):

    defaults = {"pack_mode" : "left", "character" : None}
    autoreferences = ("character", )
    required_attributes = ("character", )

    def __init__(self, **kwargs):
        super(Character_Icon, self).__init__(**kwargs)
        self.tip_bar_text = "Character: {}".format(self.character.name)

    def left_click(self, mouse):
        self.parent_application.select_target(self.character)


class Battle_Window(pride.gui.gui.Application):

    defaults = {"event" : None, "character" : None, "ability_selector" : None,
                "tip_bar_enabled" : False, "_selected_ability" : None,
                "processor" : None, "waiting" : False}
    mutable_defaults = {"participants" : dict, "_targets" : list,
                        "ready_queue" : list}
    required_attributes = ("participants", )
    autoreferences = ("battle_grid", )

    def __init__(self, **kwargs):
        super(Battle_Window, self).__init__(**kwargs)
        window = self.application_window
        grid = self.battle_grid = window.create(Battle_Grid, grid_size=(4, 4))
        # just put all characters along the diagonal
        for index, participant in enumerate(self.participants):
            participant_name = participant.name
            grid[index][index].create(Character_Icon, character=participant,
                                      text=participant_name, center_text=False)
    #        setattr(readiness_status, participant_name, False)
        #self.targets = window.create("pride.

        self.actions_menu = window.create("game3.gui.actionmenu.Action_Menu",
                                          character=self.character,
                                          pack_mode="left")
        processor = self.processor = self.create(Battle_Processor, event=self.event)
        self._children.remove(processor)
        self.processor.run()

    def accept_action(self):
        if self.waiting:
            return
        action = game3.actions.Action(source=self.character, targets=self._targets,
                                      ability=self._selected_ability, priority=1) # not finished: priority needs to be 0 for movement ability
        self._selected_ability = None
        del self._targets[:]
        self.waiting = True
        self.event.add_action(action)

    def select_ability(self, ability):
        self._selected_ability = ability
        del self._targets[:]
        self.parent_application.set_tip_bar_text("{}: Select {} targets".format(ability.name, ability.target_count))

    def setup_team(self, team_name):
        team = self.field.create(Team, h_range=(0, .10))
        self._teams[team_name] = team
        for character in self.teams[team_name]:
            team.add_character(character)

    def select_target(self, character):
        if self._selected_ability is None:
            return

        self._targets.append(character)
        _targets_len = len(self._targets)
        target_count = self._selected_ability.target_count
        if _targets_len == target_count:
            action = game3.actions.Action(source=self.character,
                                          targets=self._targets[:],
                                          ability=self._selected_ability)
            self.event.add_action(action)
        self.parent_application.set_tip_bar_text("Current target(s): ({}/{}) {}".format(_targets_len,
                                                                                        target_count,
                                                                                        ', '.join(str(target) for target in self._targets)))

    def select_target_place(self, grid_position):
        if self._selected_ability is None:
            return
        self._move_target = grid_position
        #self._targets.append(grid_position)
        #if len(self._targets) == self._selected_ability.target_count:
        action = game3.actions.Action(source=self.character,
                                      targets=(grid_position, ),
                                      ability=self._selected_ability)# to do
        self.parent_application.set_tip_bar_text("Current target: " + str(self._move_target))

    def create_abilities_menu(self):
        if self.ability_selector is None:
            self.ability_selector = self.application_window.create(Ability_Selector,
                                                                   character=self.character)
        else:
            self.ability_sheet.hide()
            self.ability_selector.show()

    def create_ability_sheet(self):
        if self.ability_sheet is None:
            pass

    def delete(self):
        self._children.append(self.processor)
        self.processor = None
        super(Battle_Window, self).delete()

import pride.gui.gui

import game3.events

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


#class Actions_Menu(pride.gui.gui.Container):
#
#    def __init__(self, **kwargs):
#        super(Actions_Menu, self).__init__(**kwargs)
#        buttons = self.create("pride.gui.gui.Container")
#        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
#                       method="use_ability", text="Use Ability", pack_mode="left",
#                       scale_to_text=False)
#        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
#                       method="ability_sheet", text="Ability Sheet", pack_mode="left",
#                       scale_to_text=False)
#        buttons.create("pride.gui.widgetlibrary.Method_Button", target=self.reference,
#                       method="status", text="View Status", pack_mode="left",
#                       scale_to_text=False)
#        self.buttons = buttons.reference
#
#    def use_ability(self):
#        self.parent_application.create_abilities_menu()
#
#    def ability_sheet(self):
#        self.parent_application.create_ability_sheet()


# make Actions Menu a tab-switched window


class Battle_Window(pride.gui.gui.Application):

    defaults = {"event" : None, "character" : None, "ability_selector" : None}
    mutable_defaults = {"teams" : dict, "_targets" : list}
    required_attributes = ("teams", )

    def __init__(self, **kwargs):
        super(Battle_Window, self).__init__(**kwargs)
        window = self.application_window
        for team in self.teams.keys():
            self.setup_team(team)

        self.actions_menu = window.create("game3.gui.actionmenu.Action_Menu", character=self.character)
        #self.status_box = window.create(Status_Box, h_range=(0, .20)).reference
        processor = self.processor = self.create(Battle_Processor, event=self.event)
        self._children.remove(processor)
        self.processor.run()

    def setup_team(self, team_name):
        self.alert("Setting up team {}".format(team_name))
        team = self.application_window.create(Team, h_range=(0, .10))
        setattr(self, "team_{}".format(team_name), team.reference)
        for character in self.teams[team_name]:
            team.add_character(character)

    def select_target(self, character):
        self._targets.append(character)
        if len(self._targets) == self._target_count:
            action = game3.actions.Action(source=self.character,
                                          targets=self._targets[:],
                                          ability=ability)
            self.event.add_action(action)
            del self._targets[:]

    def create_abilities_menu(self):
        if self.ability_selector is None:
            self.ability_selector = self.application_window.create(Ability_Selector,
                                                                   character=self.character).reference
        else:
            try:
                pride.objects[self.ability_sheet].hide()
            except KeyError:
                pass
            self.ability_selector.show()

    def create_ability_sheet(self):
        if self.ability_sheet is None:
            pass

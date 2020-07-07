# todo:
#   XP pools

# todo (pride):
#   change dropdown menu to have larger sliders

import pride.gui.gui
import pride.gui.widgets.form
import pride.gui.widgets.tabs
field_info = pride.gui.widgets.form.field_info

from pride.functions.utilities import slide
import game3.attributes
import game3.affinities
import game3.rules

def parent_sheet(self):
    character_sheet = self.parent
    while not isinstance(character_sheet, Character_Sheet):
        character_sheet = character_sheet.parent
    return character_sheet


class _Effect(pride.components.base.Base):

    #defaults = {"name" : '', "effect_type" : '', "influence" : '',
    #            "element" : '', "magnitude" : 0, "duration" : 0,
    #            "reaction" : False}

    defaults = {"influence" : "health", "element" : "blunt", "magnitude" : 1,
                "duration" : 0, "positive" : True, "do_process_reactions" : True,
                "queue_number" : 0,#STANDARD_QUEUE,
                "name" : "Unnamed Effect", "effect_type" : '',
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude},
                "trigger" : '', "target" : '', "reaction" : False}

class _Ability(pride.components.base.Base):

    defaults = {"name" : '', "homing" : False, "active_or_passive" : "active",
                "range" : 0, "target_count" : 1, "aoe" : 0, "_effects" : tuple(),
                "no_cost" : False, "effects" : tuple()}

    def _get_xp_cost(self):
        return game3.rules.calculate_ability_acquisition_cost(self)
    xp_cost = property(_get_xp_cost)

    def _get_energy_cost(self):
        null_character = game3.character.Character() # 0 affinities/grace
        return game3.rules.calculate_ability_cost(null_character, self)
    energy_cost = property(_get_energy_cost)



class _Effect_Window(pride.gui.widgets.form.Form):

    fields = [\
     [field_info("name", display_name="Name", orientation="stacked"),
      field_info("effect_type", display_name="Effect type",
                 orientation="stacked",
                 values=("damage", "heal", "buff", "debuff", "movement")),
      field_info("influence", display_name="Influence", orientation="stacked",
                 values=("health", "energy", "movement", "position") +\
                         game3.attributes.Attributes.attributes)],

     [field_info("element", display_name="Element", orientation="stacked",
                 values=game3.affinities.Affinities.affinities),
      field_info("magnitude", display_name="Magnitude"),
      field_info("duration", display_name="Duration"),
      field_info("reaction", display_name="Reaction", values=(False, True),
                 orientation="stacked")]
    ]

    defaults = {"pack_mode" : "top", "fields" : fields, "row_h_range" : (0, .1)}

    def create_subcomponents(self):
        ability = self.parent.parent.target_ability
        self.target_object = effect = _Effect()
        ability.effects += (effect, )
        self.balancer = parent_sheet(self).character.xp_pools.pools[1]
        self.include_balance_display = False
        super(_Effect_Window, self).create_subcomponents()

    def handle_value_changed(self, field, old, new):
        displayer = parent_sheet(self).abilities_pane.children[0].displayer
        displayer.entry.texture_invalid = True
        super(_Effect_Window, self).handle_value_changed(field, old, new)

    def delete(self):
        ability = self.parent.parent.target_ability
        effects = ability.effects
        effect_index = effects.index(self.target_object)
        ability.effects = effects[:effect_index] + effects[effect_index + 1:]
        super(_Effect_Window, self).delete()


class Effects_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"include_label" : True, "tab_bar_label" : "Effects",
                "new_window_type" : _Effect_Window}


class _Ability_Window(pride.gui.widgets.form.Form):

    fields = \
    [
     [field_info("name", display_name="Name", orientation="side by side",
                 compute_cost=lambda *args: 0),
      field_info("xp_cost", display_name="XP cost", orientation="stacked",
                 editable=False, w_range=(0, .1)),
      field_info("energy_cost", display_name="Energy Cost", w_range=(0, .1),
                 orientation="stacked", editable=False),
      field_info("homing", display_name="Homing", orientation="stacked",
                 w_range=(0, .1))],

     [field_info("active_or_passive", display_name="Active or Passive",
                values=("active", "passive"), orientation="stacked"),
      field_info("range", display_name="Range", orientation="stacked"),
      field_info("target_count", display_name="Target Count",
                 orientation="stacked"),
      field_info("aoe", display_name="AoE", orientation="stacked")],
    ]

    defaults = {"pack_mode" : "top", "fields" : fields, "row_h_range" : (0, .1)}
    mutable_defaults = {"target_object" : _Ability}

    def create_subcomponents(self):
        sheet = parent_sheet(self)
        self.balancer = sheet.character.xp_pools.pools[1]
        self.include_balance_display = False
        super(_Ability_Window, self).create_subcomponents()
        flag = not sheet.read_only
        self.main_window.create(Effects_Window,
                                target_ability=self.target_object,
                                include_new_tab_button=flag)

    def handle_value_changed(self, field, old, new):
        abilities_pane = parent_sheet(self).abilities_pane
        displayer = abilities_pane.children[0].displayer
        displayer.entry.texture_invalid = True
        super(_Ability_Window, self).handle_value_changed(field, old, new)

        if field.name == "name":
            tab = pride.objects[self.tab_reference]
            tab.entry.text = tab.button_text = new
            tab.pack()


class Ability_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"include_label" : True, "tab_bar_label" : "Abilities",
                "new_window_type" : _Ability_Window, "pack_mode" : "top"}


class Ability_Tree_Window(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"include_label" : True, "tab_bar_label" : "Ability Trees",
                "new_window_type" : Ability_Window, "pack_mode" : "top",
                "include_new_tab_button" : False, "read_only" : False}

    def create_subcomponents(self):
        targets = self.tab_targets = []
        window_type = self.new_window_type
        flag = self.read_only
        for count in range(4):
            def callable(*args):
                window = self.main_window.create(window_type,
                                                 read_only=flag,
                                                 include_new_tab_button=not flag)
                return window
            targets.append(callable)
        targets[0].tab_text = "Offense"
        targets[1].tab_text = "Defense"
        targets[2].tab_text = "Support"
        targets[3].tab_text = "Misc."
        super(Ability_Tree_Window, self).create_subcomponents()


class Stats_Window(pride.gui.widgets.form.Form):

    def handle_value_changed(self, field, old, new):
        parent_sheet(self).basic_info_form.synchronize_fields()
        super(Stats_Window, self).handle_value_changed(field, old, new)



class Character_Sheet(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"character" : None, "_attributes" : "Attributes",
                "_affinities" : "Affinities", "include_new_tab_button" : False,
                "stat_tab_text" : "View Stats", "read_only" : False}
    autoreferences = ("abilities_pane", "basic_info_form", "theme_editor",
                      "options")

    def create_subcomponents(self):
        assert hasattr(self, "mode")
        self._create_basic_info_fields()
        read_only = self.read_only

        character = self.character
        fields = []
        fields += self._create_attribute_fields()
        fields += self._create_affinity_fields()
        _kwargs = {"display_name" : "Stats XP"}
        form = self.main_window.create(Stats_Window,
                                       pack_mode="top", fields=fields,
                                       target_object=character,
                                       max_rows=12, row_h_range=(0, .1),
                                       balancer=character.xp_pools.pools[0],
                                       balance_display_kwargs=_kwargs,
                                       include_balance_display=True,
                                       read_only=read_only)
        callable = lambda: form
        callable.tab_text = self.stat_tab_text

        def callable2():
            abilities_pane = self.main_window.create("pride.gui.gui.Container")
            self.abilities_pane = abilities_pane
            abilities_pane.create("pride.gui.widgets.form.Form",
                                  balancer=self.character.xp_pools.pools[1],
                                  include_balance_display=True,
                                  balance_display_kwargs={"h_range" : (0, 1.0)},
                                  pack_mode="top", h_range=(0, .075),
                                  read_only=read_only)
            assert abilities_pane.children[0].displayer
            abilities_pane.create(Ability_Tree_Window, read_only=read_only)
            return abilities_pane
        callable2.tab_text = "View Abilities"

        def callable3():
            if self.mode == "creator":
                fields = [(field_info("save_and_exit",
                                    button_text="Save character and exit editor"),
                        field_info("exit_without_saving",
                                    button_text="Exit editor without saving character")
                          )]
            else:
                assert self.mode == "arcade"
                fields = [(field_info("select_character",
                                      button_text="Select this character"),
                          field_info("exit_without_saving",
                                     button_text="Exit to main menu"))]
            options = self.main_window.create("pride.gui.widgets.form.Form",
                                              fields=fields,
                                              target_object=self,
                                              row_h_range=(0, .1),
                                              read_only=read_only)
            self.options = options
            return options
        callable3.tab_text = "Finished"

        # should these be removed later?
        self.tab_targets = [callable, callable2, callable3]
        super(Character_Sheet, self).create_subcomponents()

    def _create_basic_info_fields(self):
        tiptext = (\
           "current/max health, + health restored, - incoming damage decreased",
           "current/max energy, + energy restored, - to energy costs",
           "current/max movement, + movement restored, - to movement costs")

        fields = [\
         [field_info("name", orientation="side by side",
                     display_name="Name")],
         [field_info(stat, editable=False,
                     display_name=stat[1:].title().replace('_', ' '),
                     tip_bar_text=text) for stat, text in
         zip( ("_health_info", "_energy_info", "_movement_info"), tiptext)]
         ]
        form = self.create("pride.gui.widgets.form.Form", pack_mode="top",
                           fields=fields, target_object=self.character,
                           h_range=(0, .15), read_only=self.read_only)
        self.basic_info_form = form

    def _create_xp_pool_fields(self):
        fields = [\
         [field_info("formatted", display_name=pool.name, editable=False,
                     target_object=pool) for pool in
          self.character.xp_pools.pools]
         ]
        self.create("pride.gui.widgets.form.Form", pack_mode="top",
                    fields=fields, h_range=(0, .1))

    def _create_attribute_fields(self):
        fields = [[field_info("_attributes", editable=False, target_object=self,
                             auto_create_id=False,
                             entry_kwargs={"tip_bar_text" :\
                             game3.attributes.ATTRIBUTE_DESCRIPTION,
                             "hoverable" : False,
                             "target_object" : self})]]

        _class = game3.attributes.Attributes
        _attributes = self.character.attributes
        for triplet in (("toughness", "willpower", "mobility"),
                        ("regeneration", "recovery", "recuperation"),
                        ("soak", "grace", "conditioning")):
            description = [{"tip_bar_text" : _class.description[item],
                            "minimum" : 0, "maximum" : 255,
                            "entry_kwargs" : {"include_minmax_buttons" : False},
                            "target_object" : _attributes} for item in triplet]
            fields.append(zip(triplet, description))
        return fields

    def _create_affinity_fields(self):
        description = game3.affinities.AFFINITY_DESCRIPTION
        fields = [[field_info("_affinities", editable=False, target_object=self,
                             auto_create_id=False,
                             entry_kwargs={"tip_bar_text" : description,
                                           "hoverable" : False})]]
        affinities = self.character.affinities
        for triplet in slide(game3.elements.ELEMENTS, 3):
            row = [field_info(element, target_object=affinities,
                              minimum=0, maximum=255) for
                   element in triplet]
            fields.append(row)
        return fields

    def save_and_exit(self):
        self.parent_application.save_character()

    def exit_without_saving(self):
        self.parent_application.exit_without_saving()

    def select_character(self):
        self.parent_application.select_character(self.character)


def test_Character_Sheet():
    import pride.gui
    import pride.gui.main
    import game3.rules
    game3.rules.set_rules()
    import game3.character

    character = game3.character.Character()
    window = pride.objects[pride.gui.enable()]
    sheet = lambda **kwargs: Character_Sheet(character=character, **kwargs)
    window.create(pride.gui.main.Gui, startup_programs=(sheet, ),
                  user=pride.objects["/User"])

if __name__ == "__main__":
    test_Character_Sheet()

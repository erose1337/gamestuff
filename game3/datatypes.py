import pride.components.base
import pride.gui.widgets.tabs
import pride.gui.widgets.formext
from pride.gui.widgets.form import field_info
from pride.functions.utilities import slide

import game3.rules

DEFAULT_STATS = ("toughness", "willpower", "mobility",
                 "regeneration", "recovery", "recuperation",
                 "soak", "grace", "conditioning")

ELEMENTS = ("blunt", "fire", "light",
            "slash",  "ice", "dark",
            "pierce", "electricity", "magic")

DEFAULT_STATUSES = ("health", "energy", "movement")

STAT_MINIMUM = 0
STAT_MAXIMUM = 256


class Effect(pride.gui.widgets.formext.Data):

    defaults = {"influence" : "health", "element" : "blunt", "magnitude" : 1,
                "duration" : 0, "positive" : True, "name" : '',
                "effect_type" : '',
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude},
                "trigger" : '', "target" : '', "reaction" : False}
    fields = [
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

    def _get_identifier(self):
        return tuple((name, getattr(self, name)) for name in
                     ("influence", "element", "magnitude", "duration",
                      "positive", "name", "effect_type", "trigger", "target",
                      "reaction"))
    identifier = property(_get_identifier)


class Effects(pride.gui.widgets.formext.Data):

    defaults = {"effects" : tuple()}
    row_kwargs = {0: {"h_range" : (0, .1)}}

    def __init__(self, **kwargs):
        super(Effects, self).__init__(**kwargs)
        self.tab_names = self.effects[:]


class Ability(pride.gui.widgets.formext.Data):

    defaults = {"name" : '', "homing" : False, "active_or_passive" : "active",
                "range" : 0, "target_count" : 1, "aoe" : 1,
                "no_cost" : False, "tree" : '', "energy_source" : "energy"}
    mutable_defaults = {"effects" : Effects}
    #tab_names = ("effects", )
    fields = [
         [field_info("name", display_name="Name", orientation="side by side",
                     id_kwargs={"scale_to_text" : True},
                     entry_kwargs={"scale_to_text" : False}),
          field_info("xp_cost", display_name="XP cost", orientation="stacked",
                     editable=False, w_range=(0, .1)),
          field_info("energy_cost", display_name="Energy Cost", w_range=(0, .1),
                     orientation="stacked", editable=False),
          field_info("homing", display_name="Homing", orientation="stacked",
                     w_range=(0, .1)),],

         [field_info("active_or_passive", display_name="Active or Passive",
                    values=("active", "passive"), orientation="stacked"),
          field_info("range", display_name="Range", orientation="stacked"),
          field_info("target_count", display_name="Target Count",
                     orientation="stacked"),
          field_info("aoe", display_name="AoE", orientation="stacked")],
      ]

    def _get_identifier(self):
        return tuple((name, getattr(self, name)) for name in
                     ("name", "homing", "active_or_passive", "range", "aoe",
                      "target_count", "no_cost", "tree", "energy_source")) +\
               tuple(effect.identifier for effect in self.effects)
    identifier = property(_get_identifier)

    def _get_xp_cost(self):
        return game3.rules.calculate_ability_acquisition_cost(self)
    xp_cost = property(_get_xp_cost)

    def _get_energy_cost(self):
        try:
            null_character = game3.character.Character() # 0 affinities/grace
        except NameError:
            import game3.character
            null_character = game3.character.Character()
        return game3.rules.calculate_ability_cost(null_character, self)
    energy_cost = property(_get_energy_cost)

    def __init__(self, **kwargs):
        super(Ability, self).__init__(**kwargs)
        tab_names = self.tab_names = []
        for effect in self.effects.effects:
            name = effect.name
            setattr(self, name, effect)
            tab_names.append(name)


class Abilities(pride.gui.widgets.formext.Data):

    defaults = {"abilities" : tuple(), "selected_ability" : None}
    #form_type = pride.gui.widgets.formext.Tabbed_Form
    #row_kwargs = {0: {"h_range" : (0, .25)}, 1: {"h_range" : (0, .5)}}

    def _get_selected_ability(self):
        return self._selected_ability
    def _set_selected_ability(self, value):
        self._selected_ability = value
        try:
            form = pride.objects[self.form_reference]
        except AttributeError:
            if hasattr(self, "form_reference"):
                raise
        else:
            form.view_ability(value)
    selected_ability = property(_get_selected_ability, _set_selected_ability)

    def __init__(self, **kwargs):
        super(Abilities, self).__init__(**kwargs)
        tab_names = self.tab_names = []
        for ability in self.abilities:
            name = ability.name
            setattr(self, name, ability)
            tab_names.append(name)



class Stats(pride.gui.widgets.formext.Data):

    defaults = dict((name, 0) for name in DEFAULT_STATS)
    defaults.update(dict((name, 0) for name in DEFAULT_STATUSES))

    description = {"toughness" : "Increases maximum health and helps to survive high damage",
                   "regeneration" : "Increases rate that health regenerates and provides longevity",
                   "soak" : "Decreases incoming damage",
                   "willpower" : "Increases maximum energy and enables more powerful abilities",
                   "recovery" : "Increases rate of energy recovery",
                   "grace" : "Decreases the cost of using abilities",
                   "mobility" : "Increases maximum movement points",
                   "recuperation" : "Increases rate that movement points are recuperated",
                   "conditioning" : "Decreases the cost of movement",
                   "health_info" : "current/max health, + health restored, - incoming damage decreased",
                   "energy_info" : "current/max energy, + energy restored, - to energy costs",
                   "movement_info" : "current/max movement, + movement restored, - to movement costs"}

    fields = [[field_info(name, editable=False,
                          tip_bar_text=description[name]) for name in
              ("health_info", "energy_info", "movement_info")]]

    fields += tuple([tuple([field_info(name, tip_bar_text=description[name],
                                     minimum=STAT_MINIMUM, maximum=STAT_MAXIMUM,
                                entry_kwargs={"include_minmax_buttons" : False})
                           for name in chunk])
                    for chunk in slide(DEFAULT_STATS, 3)])

    def _get__health_info(self):
        return self.format_health_stats()
    health_info = property(_get__health_info)

    def _get__energy_info(self):
        return self.format_energy_stats()
    energy_info = property(_get__energy_info)

    def _get__movement_info(self):
        return self.format_movement_stats()
    movement_info = property(_get__movement_info)

    def _get_max_health(self):
        return game3.rules.calculate_max_health(self.toughness)
    max_health = property(_get_max_health)

    def _get_max_energy(self):
        return game3.rules.calculate_max_energy(self.willpower)
    max_energy = property(_get_max_energy)

    def _get_max_movement(self):
        return game3.rules.calculate_max_movement(self.mobility)
    max_movement = property(_get_max_movement)

    def format_health_stats(self):
        attributes = self
        regen_value = game3.rules.calculate_attribute_value("regeneration", attributes.regeneration)
        soak_value = game3.rules.calculate_attribute_value("soak", attributes.soak)
        return "{}/{}, +{}, -{}".format(self.health, self.max_health,
                                        regen_value, soak_value)

    def format_energy_stats(self):
        attributes = self
        recovery_value = game3.rules.calculate_attribute_value("recovery", attributes.recovery)
        grace_value = game3.rules.calculate_attribute_value("grace", attributes.grace)
        return "{}/{}, +{}, -{}".format(self.energy, self.max_energy,
                                        recovery_value, grace_value)

    def format_movement_stats(self):
        attributes = self
        recup_value = game3.rules.calculate_attribute_value("recuperation", attributes.recuperation)
        conditioning_value = game3.rules.calculate_attribute_value("conditioning", attributes.conditioning)
        return "{}/{}, +{}, -{}".format(self.movement, self.max_movement,
                                        recup_value, conditioning_value)


class Affinities(pride.gui.widgets.formext.Data):

    defaults = dict((name, 0) for name in ELEMENTS)
    fields = tuple([tuple([field_info(name,
                                     minimum=STAT_MINIMUM, maximum=STAT_MAXIMUM,
                                entry_kwargs={"include_minmax_buttons" : False})
                         for name in chunk])
                    for chunk in slide(ELEMENTS, 3)])


class Bio_Info(pride.gui.widgets.formext.Data):

    defaults = {"name" : '', "background" : ''}
    fields = [[field_info("name", orientation="side by side",
                          id_kwargs={"scale_to_text" : True})],
              [field_info("background")]]
    row_kwargs = {0 : {"h_range" : (0, .1)}}


class Character(pride.gui.widgets.formext.Data):

    mutable_defaults = {"stats" : Stats, "affinities" : Affinities,
                        "abilities" : Abilities, "bio" : Bio_Info}
    tab_names = ("bio", "stats", "affinities", "abilities")

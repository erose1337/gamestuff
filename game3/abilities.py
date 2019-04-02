import pride.components.base

import rules
import effects

# Abilities composed out of target(s) and effect(s), and a name
# Abilities have a range, area of effect, and/or a number of targets. Abilities can be actively used or passive
# Active abilities have an activation cost

class UnusableError(Exception): pass
class PassiveActivationError(Exception): pass


class Ability(pride.components.base.Base):

    defaults = {"range" : "self", "name" : '', "effects" : tuple(), # effects holds effect types
                "no_cost" : False, "energy_source" : "energy", "homing" : False,
                "aoe" : 1, "_effects" : tuple(),} # _effects holds instances of effects
    required_attributes = ("effects", "name", )

    @classmethod
    def from_info(cls, name, **info):
        effect_list = []
        _removals = []
        assert "name" not in info
        for key, value in info.items():
            if key[:6] == "effect":
                if key == "effects":
                    continue
                assert len(value.items()) == 1
                effect_type, effect_info = value.items()[0]
                effect_list.append(getattr(effects, effect_type).from_info(**effect_info))
                _removals.append(key)
            else:
                try:
                    info[key] = int(value)
                except ValueError:
                    pass
        info["name"] = name

        if effect_list:
            info["effects"] = tuple(effect_list)
        else:
            info["effects"] = tuple(info["effects"])
        _effects = info["_effects"] = []
        for effect_type in info["effects"]:
            if effect_type.defaults["reaction"]:
                _effects.append(effect_type(target=True))
            else:
                _effects.append(effect_type())
        for key in _removals:
            del info[key]

        defaults = cls.defaults.copy()
        defaults.update(info)
        return type(name.title(), (cls, ), {"defaults" : defaults})

    @classmethod
    def add_effect(cls, effect):
        cls.defaults["effects"] += (effect, )
        if effect.defaults["reaction"]:
            _effect = effect(target=True) # effect is never applied, but target can't be Falsey
        else:
            _effect = effect()
        cls.defaults["_effects"] += (_effect, )

    @classmethod
    def remove_effect(cls, effect):
        effects = list(cls.defaults["effects"])
        index = effects.index(effect)
        del effects[index]
        _effects = list(cls.defaults["_effects"])
        assert isinstance(_effects[index], effect)
        del _effects[index]
        cls.defaults["effects"] = tuple(effects)
        cls.defaults["_effects"] = tuple(_effects)

    def activate(self, source, targets):
        effective_cost = self.calculate_ability_cost(source, targets)
        energy_source = self.energy_source
        current_energy = getattr(source, energy_source)
        if effective_cost > current_energy:
            raise ValueError("Insufficient energy for {} to activate {}".format(source.name, self.name))

        message = "{} uses {}"

        if isinstance(targets[0], tuple): # tuple implies movement effect
            assert len(targets) == 1
            print(message.format(source.name, self.name))
            for effect_type in self.effects:
                effect_type().apply(source, targets[0])
        else:
            for target in targets:
                if target != source:
                    print((message + " on {}").format(source.name, self.name, target.name))
                else:
                    print(message.format(source.name, self.name))

                distance = rules.distance_between(source.position, target.position)
                if (source != target and (not self.homing) and
                    distance > (self.range + max(0, (self.aoe - 1)))):
                    print("{} dodged {}'s {}".format(source.name, target.name, self.name))
                else:
                    for effect_type in self.effects:
                        effect_type().enqueue(source, target)
        energy_source = self.energy_source
        setattr(source, energy_source, current_energy - effective_cost)

    def calculate_ability_cost(self, source, targets):
        return rules.calculate_ability_cost(source, self)


class Active_Ability(Ability):

    defaults = {"aoe" : 1, "target_count" : 1}


class Passive_Ability(Ability):

    defaults = {"no_cost" : True, "aoe" : 0, "target_count" : 1}
    mutable_defaults = {"_active_effects" : list}
    allowed_values = {"range" : ("self", ), "target_count" : (1, )}

    def activate(self, source, target):
        if self._active_effects:
            raise PassiveActivationError("{}.activate called when already active".format(self.name))

        for effect_type in self.effects:
            effect = effect_type(duration=-1)
            self._active_effects.append(effect)
            effect.enqueue(source, target)

    def deactive(self, source, target):
        for effect in self._active_effects:
            effect.dequeue(source, target)


class Rest(Active_Ability):

    defaults = {"effects" : (effects.Rest, ), "name" : "rest", "no_cost" : True}


class Move(Active_Ability):

    defaults = {"effects" : (effects.Movement, ), "name" : "move",
                "energy_source" : "movement", "range" : "move"} # range determined by character.movement

    def calculate_ability_cost(self, source, targets):
        return rules.calculate_move_cost(source, targets[0])


class Ability_Tree(pride.components.base.Base):

    abilities = tuple()

    def __iter__(self):
        return iter(self.abilities)

    def __len__(self):
        return len(self.abilities)

    @classmethod
    def from_info(cls, tree_name, _abilities):
        return type(tree_name.title(), (cls, ),
                    {"abilities" : _abilities.keys(),
                     "mutable_defaults" : _abilities})


class Misc_Tree(Ability_Tree):

    abilities = ("rest", "move")
    mutable_defaults = {"rest" : Rest, "move" : Move}


class Regeneration(Passive_Ability):

    defaults = {"effects" : (effects.Regeneration, ),
                "name" : "regeneration"}


class Recovery(Passive_Ability):

    defaults = {"effects" : (effects.Recovery, ), "name" : "recovery"}


class Recuperation(Passive_Ability):

    defaults = {"effects" : (effects.Recuperation, ),
                "name" : "recuperation"}


class Restoration_Tree(Ability_Tree):

    abilities = ("regeneration", "recovery", "recuperation")
    mutable_defaults = {"regeneration" : Regeneration,
                        "recovery" : Recovery,
                        "recuperation" : Recuperation}


class Abilities(pride.components.base.Base):

    ability_trees = tuple()
    description = "Abilities are things your character can do.\n"\
                  "Abilities can be active or passive.\n"\
                  "   - Active abilities require energy and an action to use\n"\
                  "   - Passive abilities are always on\n"\
                  "An ability consists of a range, target count, aoe, and effects.\n"\
                  "   - range determines how far the target of an ability can be\n"\
                  "   - target count determines how many targets an ability can be used on\n"\
                  "   - aoe determines how far around the target effects will be applied\n"\
                  "   - effects determine what an ability actually does.\n"\
                  "Effects include:\n"\
                  "   - Damage effects reduce a characters health/energy/movement\n"\
                  "   - Heal effects restore a characters health/energy/movement\n"\
                  "   - Buff effects temporarily increase a characters attributes\n"\
                  "   - Debuff effects temporarily decrease a characters attributes\n"\
                  "   - Movement effects change a characters position\n"\
                  "   - Reaction effects cause other effects when triggered\n"\
                  "Effects have the following parameters:\n"\
                  "   - influence determines what stat/attribute gets affected\n"\
                  "   - magnitude determines how strong an effect is\n"\
                  "   - duration determines how long an effect lasts for\n"\
                  "   - element (damage effects only) can cause extra (or less) damage to the target\n"\
                  "More potent abilities and effects cost more to acquire and more energy to use."

    def __iter__(self):
        return iter(self.ability_trees)

    def __len__(self):
        return len(self.ability_trees) or True

    def active_abilities(self):
        output = dict()
        for tree_name in self.ability_trees:
            tree = getattr(self, tree_name)
            for ability_name in tree:
                ability = getattr(tree, ability_name)
                if isinstance(ability, Active_Ability):
                    output[tree_name + '.' + ability_name] = ability
        return output

    def passive_abilities(self):
        output = []
        for tree_name in self.ability_trees:
            tree = getattr(self, tree_name)
            for ability_name in tree:
                ability = getattr(tree, ability_name)
                if isinstance(ability, Passive_Ability):
                    output.append(ability)
        return output

    @classmethod
    def from_info(cls, **trees):
        trees.setdefault("Restoration", Restoration_Tree)
        trees.setdefault("Misc", Misc_Tree)
        return type("Abilities", (cls, ), {"ability_trees" : trees.keys(),
                                           "mutable_defaults" : trees})()

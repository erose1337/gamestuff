import pride.components.base

import game3.rules
import attributes

EFFECT_TYPES = ("damage", "heal", "rest", "buff", "debuff", "move")#, "summon")
STANDARD_QUEUE = 0
DAMAGE_QUEUE = 1
POST_QUEUE = 2
NEW_EFFECT_QUEUE = lambda: ([], [], []) # for character.mutable_defaults

class Effect(pride.components.base.Base):

    defaults = {"influence" : "health", "element" : "blunt", "magnitude" : 1,
                "duration" : 0, "positive" : True, "do_process_reactions" : True,
                "queue_number" : STANDARD_QUEUE, "name" : "Unnamed Effect",
                "effect_type" : '',
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude},
                "trigger" : '', "target" : '', "reaction" : False}

    predefaults = {"_name" : ''}

    def _get_name(self):
        return self._name or self.type_name
    def _set_name(self, value):
        self._name = value
    name = property(_get_name, _set_name)

    def _get_type_name(self):
        return self.__class__.__name__.lower()
    type_name = property(_get_type_name)

    def _get_calulation_rule(self):
        return game3.rules.calculate_effect_potency(self.type_name)
    calculation_rule = property(_get_calulation_rule)

    def enqueue(self, source, target):
        if self.reaction:
            target.reaction_effects.append(self)
        else:
            target.effect_queue[self.queue_number].append((self, source, target))

    def dequeue(self, source, target):
        if self.reaction:
            target.reaction_effects.remove(self)
        else:
            target.effect_queue[self.queue_number].remove((self, source, target))

    def apply(self, source, target):
        raise NotImplementedError()

    def evaluate_formula(self, **kwargs):
        return self.calculation_rule(**kwargs)

    def process_reaction_effects(self, source, _target):
        if _target.reaction_effects:
            for reaction in _target.reaction_effects:
                if reaction.trigger == self.type_name:
                    if reaction.target == "reacting actor":
                        reaction.apply(source, _target)
                    else:
                        assert reaction.target == "triggering actor"
                        reaction.apply(_target, source)

    @classmethod
    def from_info(cls, **info):
        for key, value in info.items():
            try:
                info[key] = int(value)
            except (ValueError, TypeError):
                continue

        defaults = cls.defaults.copy()
        defaults.update(info)
        return type(cls.__name__, (cls, ), {"defaults" : defaults})

    @classmethod
    def to_info(cls, _passive=False):
        info = dict((key, cls.defaults[key]) for key in ("influence", "magnitude",
                                                         "duration", "name")
                    if cls.defaults[key])
        if _passive:
            assert "duration" not in info
            #del info["duration"]
        if issubclass(cls, Damage):
            info["element"] = cls.defaults["element"]
        if cls.defaults["reaction"]:
            info["reaction"] = True
            info["trigger"] = cls.defaults["trigger"]
            info["target"] = cls.defaults["target"]
        #else:
        #    assert not cls.defaults["trigger"]
        #    assert not cls.defaults["target"]
        for key, value in info.items():
            info[key] = str(value)
        return info
        #return {info.pop("name") : info}


class Permanent_Effect(Effect):

    def apply(self, source, target):
        _target = target
        influence = self.influence.split('.')
        for attribute in influence[:-1]:
            target = getattr(target, attribute)
        attribute = influence[-1]

        adjustment = self.evaluate_formula(**self.formula_reagants(self, _target, source))
        if adjustment:
            if self.positive:
                adjustment = max(0, adjustment)
                sign = '+'
            else:
                adjustment = min(0, -adjustment)
                sign = '' # adjustment already has a - sign

            setattr(target, attribute, getattr(target, attribute) + adjustment)
            print("{} effect influenced {}.{} by {}{}".format(self.name, _target.name,
                                                              self.influence, sign,
                                                              adjustment))
            if source != _target and not self.reaction:
                self.process_reaction_effects(source, _target)

        self.duration -= 1
        if self.duration == -1:
            self.dequeue(source, _target)

    def unapply(self, source, target):
        return None


class Null(Effect):

    defaults = {"magnitude" : 1, "influence" : "null"}
    def apply(self, source, target):
        raise NotImplementedError("Attempted to apply Null effect")


class Damage(Permanent_Effect):

    defaults = {"influence" : "health", "positive" : False,
                "queue_number" : DAMAGE_QUEUE,
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude,
                                                      "soak" : t.attributes.soak,
                                                      "resistance" : getattr(t.affinities, e.element)}}
    required_attributes = ("element", )
    allowed_values = {"influence" : ("health", "energy", "movement")}


class Heal(Permanent_Effect):

    defaults = {"influence" : "health", "queue_number" : POST_QUEUE,
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude}}
    allowed_values = {"influence" : ("health", "energy", "movement")}


class Rest(Permanent_Effect):

    defaults = {"influence" : "energy", "magnitude" : 1, "queue_number" : POST_QUEUE,
                "formula_reagants" : lambda e, t, s: {"magnitude" : e.magnitude}}
    allowed_values = {"influence" : ("health", "energy", "movement")}


class Condition_Effect(Effect):

    defaults = {"already_applied" : False, "_adjustment" : None}

    def enqueue(self, source, target):
        if self.reaction:
            target.reaction_effects.append(self)
        else:
            target.effect_queue[self.queue_number].append((self, source, target))

    def dequeue(self, source, target):
        if self.reaction:
            target.reaction_effects.remove(self)
        else:
            target.effect_queue[self.queue_number].remove((self, source, target))

    def apply(self, source, target):
        _target = target
        if not self.already_applied:
            assert self._adjustment is None
            influence = self.influence.split('.')
            for attribute in influence[:-1]:
                target = getattr(target, attribute)
            attribute = influence[-1]

            adjustment = self.evaluate_formula(**self.formula_reagants(self, _target, source))
            if adjustment:
                if self.positive:
                    adjustment = max(0, adjustment)
                    sign = '+'
                else:
                    adjustment = min(0, -adjustment)
                    sign = '' # adjustment already has negative attached to it

                # store adjustment instead of re-calculating it. If stats change than re-calculating it can produce wrong result
                # store the difference that the effect actually caused, rather than the value of the attempted adjustment
                # e.g. 1 - 5 = 0, store -1 instead of -5
                old_value = getattr(target, attribute)
                setattr(target, attribute, old_value + adjustment)
                self._adjustment = getattr(target, attribute) - old_value

                print("{} influenced {}.{} by {}{}".format(self.name, _target.name,
                                                           self.influence, sign,
                                                           self._adjustment))
                if source != _target and self.reaction:
                    self.process_reaction_effects(source, _target)
            else:
                self._adjustment = 0
            self.already_applied = True

        self.duration -= 1
        if self.duration == -1:
            self.dequeue(source, _target)
            self.unapply(source, _target)

    def unapply(self, source, target):
        assert self.already_applied
        _target = target
        influence = self.influence.split('.')
        for attribute in influence[:-1]:
            target = getattr(target, attribute)
        attribute = influence[-1]

        adjustment = -self._adjustment
        if adjustment < 0:
            sign = ''
        else:
            sign = '+'
        setattr(target, attribute, getattr(target, attribute) + adjustment)
        print("{}.{} influenced by {}{} ({} effect expired)".format(_target.name, self.influence,
                                                                    sign, adjustment, self.name))


class Buff(Condition_Effect):

    allowed_values = {"influence" : tuple("attributes.{}".format(attribute) for
                                          attribute in attributes.Attributes.attributes)}


class Debuff(Condition_Effect):

    defaults = {"positive" : False}
    allowed_values = {"influence" : tuple("attributes.{}".format(attribute) for
                                          attribute in attributes.Attributes.attributes)}


class Movement(Permanent_Effect):

    defaults = {"influence" : "position", "magnitude" : -1}
    allowed_values = {"influence" : ("position", )}

    def enqueue(self, source, target):
        source.effect_queue[self.queue_number].append((self, source, target))

    def dequeue(self, source, target):
        source.effect_queue[self.queue_number].remove((self, source, target))

    def apply(self, source, target):
        # to do: check to make sure target is within movement range indicated by level
        source.position = target
        print("{} moved to {}".format(source.name, target))
        #self.dequeue(source, target)


class Passive(Condition_Effect):

    defaults = {"duration" : -1}


class Restorative_Effect(Heal):
    # magnitude determined by attributes; required_attributes will complain if magnitude == 0
    defaults = {"queue_number" : POST_QUEUE, "magnitude" : -1}


class Regeneration(Restorative_Effect):

    defaults = {"influence" : "health",
                "formula_reagants" : lambda e, t, s: {"magnitude" : t.attributes.regeneration}}


class Recovery(Restorative_Effect):

    defaults = {"influence" : "energy",
                "formula_reagants" : lambda e, t, s: {"magnitude" : t.attributes.recovery}}


class Recuperation(Restorative_Effect):

    defaults = {"influence" : "movement",
                "formula_reagants" : lambda e, t, s: {"magnitude" : t.attributes.recuperation}}

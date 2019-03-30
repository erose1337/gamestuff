import pride.components.base

class Attributes(pride.components.base.Base):

    attributes = ("toughness", "regeneration", "soak",
                  "willpower", "recovery", "grace",
                  "mobility", "recuperation", "conditioning")
    predefaults = dict(('_' + name, 0) for name in attributes)
    defaults = dict((name, 0) for name in attributes)
    description = {"toughness" : "Increases maximum health and helps to survive high damage",
                   "regeneration" : "Increases rate that health regenerates and provides longevity",
                   "soak" : "Decreases incoming damage",
                   "willpower" : "Increases maximum energy and enables more powerful abilities",
                   "recovery" : "Increases rate of energy recovery",
                   "grace" : "Decreases the cost of using abilities",
                   "mobility" : "Increases maximum movement points",
                   "recuperation" : "Increases rate that movement points are recuperated",
                   "conditioning" : "Decreases the cost of movement"}

    # turns all attributes into descriptors
    for attribute in attributes:
        def getter(self, _attribute=attribute):
            return getattr(self, '_' + _attribute)
        def setter(self, value, _attribute=attribute):
            setattr(self, '_' + _attribute, max(0, value))

        vars()["_get_{}".format(attribute)] = getter
        vars()["_set_{}".format(attribute)] = setter
        vars()[attribute] = property(getter, setter)

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def items(self):
        return ((attribute, getattr(self, attribute)) for attribute in self.attributes)

    def format_attributes(self):
        output = ''
        line = "\n{}: {}{:>26}: {}{:>26}: {}"
        output += line.format("toughness", self.toughness,
                              "willpower", self.willpower,
                              "mobility", self.mobility)
        output += line.format("regeneration", self.regeneration,
                              "recovery", self.recovery,
                              "recuperation", self.recuperation)
        output += line.format("soak", self.soak,
                              "grace", self.grace,
                              "conditioning", self.conditioning)
        return output

    @classmethod
    def format_descriptions(cls):
        description = cls.description
        return '\n'.join("{}: {}".format(name, description[name]) for name in cls.attributes)

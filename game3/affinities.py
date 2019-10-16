import pride.components.base
from pride.functions.utilities import slide

import elements

AFFINITY_DESCRIPTION = "Affinity for a given element provides an energy discount when using damage effects with that element, "\
                       "and decreases incoming damage from damage effects of that element"

class Affinities(pride.components.base.Base):

    affinities = elements.ELEMENTS
    defaults = dict((element, 0) for element in affinities)
    description = "Affinities provide extra resistance against elements and a discount when using effects with those elements"

    def __iter__(self):
        return iter(self.affinities)

    def __len__(self):
        return len(self.affinities)

    def items(self):
        return ((attribute, getattr(self, attribute)) for attribute in self.affinities)

    def format_affinities(self):
        output = ''
        line = "\n{}: {}{:>26}: {}{:>26}: {}"
        for a, b, c in slide(self.affinities, 3):
            output += line.format(a, getattr(self, a),
                                  b, getattr(self, b),
                                  c, getattr(self, c))
        return output

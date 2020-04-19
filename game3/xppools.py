import pride.components.base
import pride.gui.widgets.form

import game3.rules
import game3.elements

DEFAULT_POOLS = ("stats", "abilities", "equipment")


class XP_Pool(pride.gui.widgets.form.Balancer):

    _starting_xp = game3.rules.RULES["character creation"]["starting_xp_amount"]()

    def __init__(self, name, balance=_starting_xp, total=_starting_xp):
        if balance < total:
            raise ValueError("balance exceeds total")
        super(XP_Pool, self).__init__(name, balance)
        self.total = total

    def _get_formatted(self):
        return "{}/{}".format(self.balance, self.total)
    formatted = property(_get_formatted)

    def earn(self, amount):
        self.balance += amount
        self.total += amount

    def compute_cost(self, field, old_value, new_value):
        return super(XP_Pool, self).compute_cost(field, old_value, new_value)


class Stat_XP_Pool(XP_Pool):

    def compute_cost(self, field, old_value, new_value):
        assert old_value != new_value
        name = field.name
        costf = game3.rules.calculate_stat_acquisition_cost
        if name in game3.elements.ELEMENTS:
            name = "affinity"

        if new_value < old_value:
            cost = -sum(costf(name, x) for x in range(old_value, new_value, -1))
            #print("refund {} for downgrading {} -> {}".format(cost, old_value, new_value))
        else:
            cost = sum(costf(name, x) for x in range(old_value + 1, new_value + 1))
            #print("cost {} for upgrading {} -> {}".format(cost, old_value, new_value))
        return cost


class Abilities_XP_Pool(XP_Pool):

    def compute_cost(self, field, old, new):
        return super(Abilities_XP_Pool, self).compute_cost(field, old, new)


class Equipment_XP_Pool(XP_Pool):

    def compute_cost(self, field, old, new):
        return super(Equipment_XP_Pool, self).compute_cost(field, old, new)


class XP_Pools(pride.components.base.Base):

    mutable_defaults = {"pools" : lambda:\
                         tuple(_type(name=name) for name, _type in
                               zip(DEFAULT_POOLS,
                                   (Stat_XP_Pool,
                                    Abilities_XP_Pool,
                                    Equipment_XP_Pool)
                                   )
                              )
                        }

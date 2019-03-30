import pride.components.base

import effects
import elements
import abilities

TARGET_SELF = ("self", )
TARGET_CLOSE = ("close", )
TARGET_FAR = ("far", )
TARGET_AOE = ("aoe", )
TARGET_MULTITARGET = ("multitarget", )
TARGET_NULL = tuple()

MOVEMENT_SKILLS = ("physical", "flight", "teleport")
OFFENSE_SKILLS = ("hand_to_hand", "melee_weapon", "ranged_attack")
DEFENSE_SKILLS = ("defend", ) + tuple("resist_{}".format(element) for element in elements.ELEMENTS)
MISC_SKILLS = ("rest", "heal")

class Skill_Tree(pride.components.base.Base):

    skills = tuple()

    def __iter__(self):
        return iter(self.skills)

    def __len__(self):
        return len(self.skills)


class Skill(abilities.Ability): pass


class Movement(Skill):

    defaults = {"target_type" : TARGET_FAR, "effects" : (effects.Move(), ),
                "trigger" : abilities.TRIGGER_ACTIVE}

class Physical(Movement): pass
class Flight(Movement): pass
class Teleport(Movement): pass

class Movement_Skills(Skill_Tree):

    skills = ("physical", "flight", "teleport")
    mutable_defaults = {"physical" : Physical, "flight" : Flight, "teleport" : Teleport}


class Offense(Skill):

    defaults = {"target_type" : TARGET_CLOSE, "effects" : (effects.Damage(), ),
                "element" : elements.ELEMENT_BLUNT,
                "trigger" : abilities.TRIGGER_ACTIVE}

class Hand_To_Hand(Offense): pass
class Melee_Weapon(Offense): pass
class Ranged_Attack(Offense): defaults = {"target_type" : TARGET_FAR}

class Offense_Skills(Skill_Tree):

    skills = ("hand_to_hand", "melee_weapon", "ranged_attack")
    mutable_defaults = {"hand_to_hand" : Hand_To_Hand, "melee_weapon" : Melee_Weapon,
                        "ranged_attack" : Ranged_Attack}


class Defense(Skill):

    defaults = {"target_type" : TARGET_SELF}

class Defend(Defense):

    defaults = {"effects" : (effects.Buff(influence="attributes.soak"), ),
                "trigger" : abilities.TRIGGER_ACTIVE}

class Defense_Skills(Skill_Tree):

    skills = ("defend", )
    mutable_defaults = {"defend" : Defend}



class Resist(Skill):

    defaults = {"target_type" : TARGET_SELF, "effects" : (effects.Null(influence="resist"), ),
                "trigger" : abilities.TRIGGER_PASSIVE}

    def use(self, source, target):
        raise TypeError("Cannot 'use' Resist skills")

class _RESIST_STORAGE(object): pass

for element in elements.ELEMENTS:
    skill_name = "Resist_{}".format(element.title())
    skill_class = type(skill_name, (Resist, ), dict())
    setattr(_RESIST_STORAGE, skill_name, skill_class)
del element, skill_name, skill_class

class Resist_Skills(Skill_Tree):

    skills = elements.ELEMENTS
    mutable_defaults = dict()
    for entry in elements.ELEMENTS:
        class_name = "Resist_{}".format(entry.title())
        mutable_defaults[entry] = getattr(_RESIST_STORAGE, class_name)


class Misc(Skill):

    defaults = {"target_type" : TARGET_SELF, "trigger" : abilities.TRIGGER_ACTIVE}

class Rest(Misc):

    defaults = {"effects" : (effects.Rest(), )}

class Heal(Misc):

    defaults = {"effects" : (effects.Heal(), )}


class Misc_Skills(Skill_Tree):

    skills = ("rest", "heal")
    mutable_defaults = {"rest" : Rest, "heal" : Heal}


class Skills(pride.components.base.Base):

    skill_trees = ("movement", "offense", "defense", "resists", "misc")
    mutable_defaults = {"movement" : Movement_Skills, "offense" : Offense_Skills,
                        "defense" : Defense_Skills, "resists" : Resist_Skills,
                        "misc" : Misc_Skills}

    def __iter__(self):
        return iter(self.skill_trees)

    def __len__(self):
        return len(self.skill_trees)

    def skillset(self):
        output = dict()
        for tree_name in self.skill_trees:
            tree = getattr(self, tree_name)
            for skill_name in tree:
                skill = getattr(tree, skill_name)
                if skill.level:
                    output[tree_name + '.' + skill_name] = skill
        return output

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import cefparser

import expreval
import attributes
import affinities
import abilities

class InvalidFunctionName(Exception): pass
class InvalidAbilityInfo(Exception): pass
class InvalidEffectInfo(Exception): pass

ABILITY_DISALLOW = ("no_cost", )
EFFECT_DISALLOW = ("queue_number", "_adjustment")

def parse_filename(filename, ability_disallow=ABILITY_DISALLOW,
                    effect_disallow=EFFECT_DISALLOW):
    info = cefparser.parse_filename(filename)
    return parse_info(info, ability_disallow, effect_disallow)

def parse_file(_file, ability_disallow=ABILITY_DISALLOW,
               effect_disallow=EFFECT_DISALLOW):
    info = cefparser.parse(_file)
    return parse_info(info, ability_disallow, effect_disallow)

def parse_bytes(_file_bytes, ability_disallow=ABILITY_DISALLOW,
                effect_disallow=EFFECT_DISALLOW):
    _file = StringIO.StringIO(_file_bytes)
    _file.seek(0)
    return parse_file(_file, ability_disallow, effect_disallow)

def parse_info(info, ability_disallow=ABILITY_DISALLOW,
               effect_disallow=EFFECT_DISALLOW):
    character_info = info["Character Info"]
    _attributes = parse_attributes(character_info)
    _affinities = parse_affinities(character_info)
    if "Abilities" in info:
        _abilities = parse_abilities(info, ability_disallow=ability_disallow,
                                    effect_disallow=effect_disallow)
    else:
        _abilities = abilities.Abilities()
    return {"name" : character_info["Basic Info"]["name"],
            "xp" : int(character_info["Basic Info"].get("xp", 0)),
            "attributes" : _attributes, "affinities" : _affinities,
            "abilities" : _abilities}

def parse_attributes(character_info):
    attribute_info = dict()
    for key, value in character_info["Attributes"].items():
        attribute_info[key.lower().replace(' ', '_')] = int(value)
    return attributes.Attributes(**attribute_info)

def parse_affinities(character_info):
    affinity_info = dict()
    for key, value in character_info["Affinities"].items():
        affinity_info[key.lower()] = int(value)
    return affinities.Affinities(**affinity_info)

def parse_abilities(info, ability_disallow=ABILITY_DISALLOW,
                    effect_disallow=EFFECT_DISALLOW):
    trees = dict()
    for tree_name, ability_listing in info["Abilities"].items():
        #tree_name = tree_name.replace(' ', '_')
        ability_objects = dict()
        for ability_name, ability_info in ability_listing.items():
            #ability_name = ability_name.replace(' ', '_')
            ability_objects[ability_name] = parse_ability(ability_name, ability_info,
                                                          ability_disallow,
                                                          effect_disallow)
        trees[tree_name] = abilities.Ability_Tree.from_info(tree_name, ability_objects)
    return abilities.Abilities.from_info(**trees)

def parse_ability(ability_name, ability_info, ability_disallow=ABILITY_DISALLOW,
                  effect_disallow=EFFECT_DISALLOW):
    for forbidden in ability_disallow:
        if forbidden in ability_info:
            raise InvalidAbilityInfo("Cannot set {} attribute on ability '{}' (file {})".format(forbidden, ability_name, filename))
    for key, value in ability_info.items():
        if key[:6] == "effect":
            _values = value.values()[0]
            for forbidden in effect_disallow:
                if forbidden in _values:
                    raise InvalidEffectInfo("Cannot set {} on effect {}.{} (file {})".format(forbidden, ability_name, key, filename))
    #ability_name = ability_name.replace(' ', '_')
    if ability_info.get("passive", "False").lower() == "true":
        ability_type = abilities.Passive_Ability
    else:
        ability_type = abilities.Active_Ability
    return ability_type.from_info(ability_name, **ability_info)

def parse_rules(filename):
    output = dict()

    info = cefparser.parse_filename(filename)
    functions = info.pop("Functions")
    for function_name, body in functions.items():
        assert len(body) == 1
        assert 'x' in body
        if ' ' in function_name:
            raise InvalidFunctionName("Error parsing rules; Space found in function name '{}'".format(function_name))
        functions[function_name] = (expreval.Monovariate_Function(body['x'], 'x'), 1)

    for category, entries in info.items():
        output[category.lower()] = rule_info = dict()
        for entry, fields in entries.items():
            entry = entry.lower().replace(' ', '_')
            for field, expr in fields.items():
                key = "{}_{}".format(entry, field.replace(' ', '_'))
                rule_info[key] = expreval.Expression(expr, functions)

    return output

if __name__ == "__main__":
    character_info = parse_filename("demochar.cef")
    rules = parse_rules("rules.cef")
    print rules["abilities"]["abilities_energy_cost"](range=1, aoe=1, targets=1, effect_cost=1, grace=1)
    print rules["attributes"]["max_health_value"](level=10)
    print rules["abilities"]["influence_max_health_cost"]()

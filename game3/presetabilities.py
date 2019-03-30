import itertools

import parsing

# create abilities by combining different "traits"

HOMING_TRAITS = ("guided", "unguided")
RANGE_TRAITS = ("far", "close", "personal", "self")
TARGET_COUNT_TRAITS = ("swarm", "flurry", "single target")
AOE_TRAITS = ("explosive", "group", "precise")
MAGNITUDE_TRAITS = ("nuke", "burn", "chip")
DURATION_TRAITS = ("chronic", "persistent", "instant")
INFLUENCE_TRAITS = ("wounding", "draining", "holding", "debilitating", "depression",
                    "crippling", "sickness", "exhaustion", "fatigue", "weakening",
                    "clumsiness", "lethargy")#, "aversion")
TRAITS = (HOMING_TRAITS, RANGE_TRAITS, TARGET_COUNT_TRAITS, AOE_TRAITS,
          MAGNITUDE_TRAITS, DURATION_TRAITS, INFLUENCE_TRAITS)

HOMING = {"guided" : True, "unguided" : False}
RANGE = {"self" : "self", "personal" : 0, "close" : 2, "far" : 3}
TARGET_COUNT = {"swarm" : 3, "flurry" : 2, "single target" : 1}
AOE = {"explosive" : 3, "group" : 2, "precise" : 1}
MAGNITUDE = {"nuke" : 3, "burn" : 2, "chip" : 1}
DURATION = {"chronic" : 3, "persistent" : 2, "instant" : 1}
INFLUENCE = {"debilitating" : "toughness", "depression" : "willpower", "crippling" : "mobility",
             "sickness" : "regeneration", "exhaustion" : "recovery", "fatigue" : "recuperation",
             "weakening" : "soak", "clumsiness" : "grace", "lethargy" : "conditioning"}
INFLUENCE.update(dict((key, "attributes.{}".format(value)) for key, value in INFLUENCE.items()))
INFLUENCE.update({"wounding" : "health", "draining" : "energy", "holding" : "movement"})
             #"aversion" : "affinity"
def create_presets(all_traits=TRAITS):
    outputs = []
    for traits in itertools.product(*all_traits):
        (homing, range, targets, aoe,
         magnitude, duration, influence) = traits
        ability_info = {"homing" : HOMING[homing],
                        "range" : RANGE[range],
                        "target_count" : TARGET_COUNT[targets],
                        "aoe" : AOE[aoe]}
        influence = INFLUENCE[influence]
        effect_info = {"magnitude" : MAGNITUDE[magnitude],
                       "duration" : DURATION[duration],
                       "influence" : influence}
        if influence in ("health", "energy", "movement"):
            info = ability_info.copy()
            info["effect1"] = {"Damage" : effect_info}
            outputs.append(parsing.parse_ability("preset damage ability", info)())
            info = ability_info.copy()
            info["effect1"] = {"Heal" : effect_info}
            outputs.append(parsing.parse_ability("preset heal ability", info)())
        else:
            info = ability_info.copy()
            info["effect1"] = {"Buff" : effect_info}
            outputs.append(parsing.parse_ability("preset buff ability", info)())
            info = ability_info.copy()
            info["effect1"] = {"Debuff" : effect_info}
            outputs.append(parsing.parse_ability("preset debuff ability", info)())
    return outputs

if __name__ == "__main__":
    print create_presets()[0]

import game3.rules

def test():
    game3.rules.set_game3.rules()

    import character
    c = character.Character.from_sheet("demochar3.cef")
    c.to_sheet("demochar4.cef")
    c2 = character.Character.from_sheet("demochar4.cef")
    assert c.name == c2.name
    for attribute_name in c.attributes:
        assert getattr(c.attributes, attribute_name) == getattr(c2.attributes, attribute_name)
    for affinity_name in c.affinities:
        assert getattr(c.affinities, affinity_name) == getattr(c2.affinities, affinity_name)
    for tree_name in c.abilities:
        tree1 = getattr(c.abilities, tree_name)
        tree2 = getattr(c2.abilities, tree_name)
        for ability_name in tree1:
            ability1 = getattr(tree1, ability_name)
            ability2 = getattr(tree2, ability_name)
            for key, value in ability1.defaults.items():
                if key not in ("effects", "_effects"):
                    assert value == ability2.defaults[key], (value, ability2.defaults[key], key)
                elif key == "effects":
                    value2 = ability2.defaults["effects"]
                    for index, effect1 in enumerate(value):
                        for effect2 in value2: # order is not preserved; can only ensure that *some* effect matches
                            success = False
                            for _key, _value in effect1.defaults.items():
                                if _value == effect2.defaults[_key]:
                                    success = True
                                    break
                            if success:
                                break
                        else:
                            raise ValueError("Failed to find matching effect in ability '{}'".format(ability_name))

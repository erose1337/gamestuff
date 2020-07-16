import pride.gui.widgets.formext
from pride.gui.widgets.form import field_info
from pride.functions.utilities import slide

class Sheet(pride.gui.widgets.formext.Tabbed_Form): pass


def test_Sheet():
    import pride.gui
    import pride.gui.main
    import game3.rules
    game3.rules.set_rules()
    import game3.character
    import game3.datatypes

    _effects = (game3.datatypes.Effect(name="test_effect1"), )
    effects = game3.datatypes.Effects(effects=_effects)
    test_ability = game3.datatypes.Ability(name="test_ability", effects=effects)

    test_ability2 = game3.datatypes.Ability(name="test_ability2")
    test_ability3 = game3.datatypes.Ability(name="test_ability3")
    abilities = game3.datatypes.Abilities(abilities=(test_ability,
                                                     test_ability2,
                                                     test_ability3))
    character = game3.datatypes.Character(abilities=abilities)
    window = pride.objects[pride.gui.enable()]
    sheet = lambda **kwargs: Sheet(target_object=character, **kwargs)
    window.create(pride.gui.main.Gui, startup_programs=(sheet, ),
                  user=pride.objects["/User"])

if __name__ == "__main__":
    test_Sheet()

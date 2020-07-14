import pride.gui.widgets.tabs
from pride.gui.widgets.form import field_info
from pride.functions.utilities import slide

class Sheet(pride.gui.widgets.tabs.Tabbed_Window):

    defaults = {"character" : None,
                "default_form_type" : "pride.gui.widgets.form.Form"}

    def create_subcomponents(self):
        tab_targets = self.tab_targets = []
        for name in self.character.listing:

            def callable(name=name):
                values = getattr(self.character, name)
                try:
                    fields = values.fields
                except AttributeError:
                    fields = [[field_info(_name) for _name in chunk]
                               for chunk in slide(values.listing, 3)]
                try:
                    row_kwargs = values.row_kwargs
                except AttributeError:
                    row_kwargs = dict()

                try:
                    form_type = values.form_type
                except AttributeError:
                    form_type = self.default_form_type
                
                form = self.main_window.create(form_type, fields=fields,
                                               target_object=values,
                                               row_kwargs=row_kwargs)
                values.form_reference = form.reference
                return form
            callable.tab_text = name
            tab_targets.append(callable)
        super(Sheet, self).create_subcomponents()

def test_Sheet():
    import pride.gui
    import pride.gui.main
    import game3.rules
    game3.rules.set_rules()
    import game3.character
    import game3.datatypes

    test_ability = game3.datatypes.Ability(name="test ability")
    ability2 = game3.datatypes.Ability(name="test ability2")
    ability3 = game3.datatypes.Ability(name="test ability3")
    abilities = game3.datatypes.Abilities(abilities=("test_ability",
                                                     "test_ability2",
                                                     "test_ability3"),
                                          test_ability=test_ability,
                                          test_ability2=ability2,
                                          test_ability3=ability3)
    character = game3.datatypes.Character(abilities=abilities)
    window = pride.objects[pride.gui.enable()]
    sheet = lambda **kwargs: Sheet(character=character, **kwargs)
    window.create(pride.gui.main.Gui, startup_programs=(sheet, ),
                  user=pride.objects["/User"])

if __name__ == "__main__":
    test_Sheet()

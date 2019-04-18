import argparse

ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument("-r", "--rules", help="Specify a custom rule set file")

def main():
    import rules
    args, _ = ARGPARSER.parse_known_args()
    rules_filename = args.rules or "rules.cef"
    rules.set_rules(rules_filename)

    #import events
    #events.test_battle()

    #import character
    #char = character.Character.from_sheet("demochar3.cef")
    #char.to_sheet("demochar4.cef")

    import pride.gui
    import game3.gui.window
    window = pride.gui.enable()
    game = pride.objects[window].create(game3.gui.window.Game_Window)

if __name__ == "__main__":
    main()

import argparse

ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument("-r", "--rules", help="Specify a custom rule set file")

def main():
    import game3.rules
    args, _ = ARGPARSER.parse_known_args()
    rules_filename = args.rules or "rules.cef"
    game3.rules.set_rules(rules_filename)
    #import events
    #events.test_battle()

    #import character
    #char = character.Character.from_sheet("demochar3.cef")
    #char.to_sheet("demochar4.cef")

    import pride.gui
    import game3.engine.server
    import game3.engine.client
    sdl_window = pride.objects[pride.gui.enable()]

    pride.objects["/Python"].create(game3.engine.server.Game_Server)
    client = pride.objects["/User"].create(game3.engine.client.Game_Client,
                                           sdl_window=sdl_window, username="Ella")

    #game = pride.objects[window].create(game3.gui.window.Game_Window)

if __name__ == "__main__":
    main()

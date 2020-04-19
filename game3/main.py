import argparse

import pride.gui
import pride.gui.main
ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument("-r", "--rules", help="Specify a custom rule set file")

import game3.rules

class Launcher(pride.gui.main.Gui):

    def launch_programs(self):
        super(Launcher, self).launch_programs()
        pride.objects["/Python"].create("game3.engine.server.Game_Server")
        client = self.user.create("game3.engine.client.Game_Client",
                                  sdl_window=self.sdl_window,
                                  username=self.user.username, auto_register=True)


def main():
    args, _ = ARGPARSER.parse_known_args()
    rules_filename = args.rules or game3.rules.RULES_FILE
    game3.rules.set_rules(rules_filename)

    window = pride.objects[pride.gui.enable(x=50, y=65)]
    launcher = window.create(Launcher, user=pride.objects["/User"])
                                            # required access: "device"
                                            # does not require username/password

if __name__ == "__main__":
    main()

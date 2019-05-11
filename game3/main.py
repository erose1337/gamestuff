import argparse

import pride.gui
import pride.gui.main
ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument("-r", "--rules", help="Specify a custom rule set file")

import game3.rules

class Test_User(pride.components.user.User):
    # possible to make a `@not_in_production` decorator?
    defaults = {"kdf_iterations" : 1}


class Launcher(pride.gui.main.Gui):

    defaults = {"user_type" : Test_User}

    def login_success(self, username):
        super(Launcher, self).login_success(username)
        pride.objects["/Python"].create("game3.engine.server.Game_Server")
        client = self.user.create("game3.engine.client.Game_Client",
                                  sdl_window=pride.objects[self.sdl_window],
                                  username=username, auto_register=True)
        self.delete()



def main():
    args, _ = ARGPARSER.parse_known_args()
    rules_filename = args.rules or "rules.cef"
    game3.rules.set_rules(rules_filename)

    window = pride.objects[pride.gui.enable()]
    window.create(Launcher)
    print("Created game window for testing (using insecure Test_User)")

if __name__ == "__main__":
    main()

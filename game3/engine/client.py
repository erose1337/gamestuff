import pride.components.authentication3

import game3.character

remote_procedure_call = pride.components.authentication3.remote_procedure_call

class Game_Client(pride.components.authentication3.Authenticated_Client):

    defaults = {"sdl_window" : None, "target_service" : "/Python/Game_Server",
                "game_window_type" : "game3.gui.window2.Game_Window"}
    verbosity = {"login_success" : "vv", "login_failure" : "vv", "login" : "vv"}
    autoreferences = ("sdl_window", )
    required_attributes = ("sdl_window", )

    def __init__(self, **kwargs):
        super(Game_Client, self).__init__(**kwargs)
        window = self.game_window = self.sdl_window.create(self.game_window_type,
                                                           game_client=self)
        window.show_status("Connecting...")

    def login_success(self, login_message):
        self.game_window.show_status("Logged in successfully")
        super(Game_Client, self).login_success(login_message)
        self.show_initial_window()

    def show_initial_window(self):
        self.game_window.load_initial_window()

    @remote_procedure_call(callback_name="show_character_screen_arcade")
    def get_character_info(self): pass

    def show_character_screen_arcade(self, character_info):
        window = self.game_window
        window.clear_status()#set_status("Drawing characters...", fade_out=False)
        #print type(character_info), character_info
        characters = [game3.character.Character.from_bytes(info) for info in character_info]
        window.load_character_selection_screen(characters)

    # character_screen calls select_character when appropriate
    @remote_procedure_call(callback_name="character_selected")
    def select_character(self, name): pass

    def character_selected(self, result):
        self.game_window.show_status("Character selected")

    @remote_procedure_call(callback_name="save_character_result")
    def save_character(self, name, character_sheet): pass

    def save_character_result(self, result):
        self.game_window.show_status("Save character result: {}".format(result))

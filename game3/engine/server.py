try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import pride.components.authentication3

class Game_Server(pride.components.authentication3.Authenticated_Service):

    database_structure = {"Character" : ("userid BLOB PRIMARY_KEY",
                                         "name TEXT", "info BLOB")}
    mutable_defaults = {"map_info" : dict, "active_character" : dict}
    remotely_available_procedures = ("get_character_info", "select_character",
                                     "get_map_info", "save_character")

    def get_character_info(self):
        user = self.current_user
        characters = self.database.query("Character",
                                         retrieve_fields=("info", ),
                                         where={"userid" : user})
        if characters and len(characters[0]) == 1 and isinstance(characters[0], tuple):
            characters = [item[0] for item in characters]
        elif isinstance(characters, str):
            characters = [characters]
        return characters

    def select_character(self, name):
        user = self.current_user
        data = self.database.query("Character", retrieve_fields=("info", ),
                                   where={"userid" : current_user, "name" : name})
        character_info = cefparser.parse(StringIO.StringIO(data))
        _character = character.Character(**character_info)
        self.active_character[user] = _character

    def save_character(self, name, character_sheet):
        user = self.current_user
        result = self.database.insert_or_replace("Character", (user, name, character_sheet))
        return "Success"

    def get_map_info(self):
        return self.map_info

    #def join_event(self, location, event_name):
    #    event = self.map_info[location][event_name]

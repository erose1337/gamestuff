try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import pride.components.authentication3

class Game_Server(pride.components.authentication3.Authenticated_Service):

    database_structure = {"Character" : ("identifier BLOB PRIMARY_KEY",
                                         "name TEXT",
                                         "info BLOB")}
    mutable_defaults = {"map_info" : dict, "active_character" : dict}
    remotely_available_procedures = ("get_character_info", "select_character",
                                     "get_map_info")
    def get_character_info(self):
        user = self.current_user
        characters = self.database.query("Character",
                                         retrieve_fields=("name", "info"),
                                         where={"identifier" : user})
        return characters

    def select_character(self, name):
        user = self.current_user
        data = self.database.query("Character", retrieve_fields=("info", ),
                                   where={"identifier" : current_user, "name" : name})
        character_info = cefparser.parse(StringIO.StringIO(data))
        _character = character.Character(**character_info)
        self.active_character[user] = _character

    def get_map_info(self):
        return self.map_info

    #def join_event(self, location, event_name):
    #    event = self.map_info[location][event_name]

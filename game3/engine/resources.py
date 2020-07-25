import hashlib

import pride.components.database

class Game3_Client_Resources(pride.components.database.Database):

    defaults = {"hash_algo" : "sha256", "id_size" : 8}
    schema = {"abilities" : ("id BLOB PRIMARY_KEY UNIQUE",
                             "name TEXT", "homing INTEGER",
                             "passive INTEGER", "range INTEGER",
                             "target_count INTEGER", "aoe INTEGER",
                             "tree TEXT", "energy_source TEXT",
                             "influence TEXT", "element TEXT",
                             "magnitude INTEGER", "duration INTEGER",
                             "effect_type TEXT", "trigger TEXT",
                             "target TEXT", "reaction INTEGER")}

    def add_ability(self, ability):
        identifier = self.hash_f(ability.identifier)
        exists = self.query("abilities", where={"id" : identifier})
        if exists:
            return
        self.insert_into("abilities", (identifier, ability.name,
                         ability.homing, ability.passive, ability.range,
                         ability.target_count, ability.aoe, ability.tree,
                         ability.energy_source, ability.influence,
                         ability.element, ability.magnitude,
                         ability.duration, ability.effect_type,
                         ability.trigger, ability.target, ability.reaction))

    def hash_f(self, _bytes):
        return getattr(hashlib, self.hash_algo)(_bytes).hexdigest()[self.id_size]

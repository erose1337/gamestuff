# drop table:
#   contains items that can be dropped
# drop item:
#   select x items from table at random
# drop chance:
#   determined by number of items in table
#   add item to table multiple times -> greater drop rate
import game.mechanics.randomgeneration

class Drop_Table(object):
       
    possible_drops = tuple()
    
    @classmethod
    def drop_item(cls, amount):
        possible_drops = cls.possible_drops
        return [game.mechanics.randomgeneration.random_selection(possible_drops) for count in range(amount)]
        
import pride.components.base

class Level(pride.components.base.Base):
    
    defaults = {"progress" : 0}
    flags = {"_value" : 1, "_progress" : 0}
    max_level = 256
    level_structure = dict((x, 10 ** x) for x in range(max_level))
    verbosity = {"value_increased" : 0}
    
    def _get_progress(self):
        return self._progress
    def _set_progress(self, progress, level_structure=level_structure):
        self._progress = progress
        if progress > level_structure[self.value]:
            self._value += 1
            self.alert("value increased", level=self.verbosity["value_increased"])
            
    progress = property(_get_progress, _set_progress)
    
    def _get_value(self):
        return self._value
    def _set_value(self, value):
        raise AttributeError("Unable to set level; Level determined by progress")
    value = property(_get_value, _set_value)
    
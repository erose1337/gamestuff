#put rotating stars (points) in background
import itertools
import random

import pride.gui.gui

import sdl2

def random_position(area, randsize=2 ** 32):
    _x, _y, _w, _h = area
    x_max = _x + _w
    y_max = _y + _h
    x = random.randint(0, randsize) % x_max
    while x > x_max and x < _x:
        x = random.randint(0, randsize) % x_max

    y = random.randint(0, randsize) % y_max
    while y > y_max and y < _y:
        y = random.randint(0, randsize) % y_max
    return x, y


class Star_Theme(pride.gui.gui.Theme):

    defaults = {"angle" : 10.0, "angle_change" : -.5}

    def draw_texture(self):
        x, y, w, h = area = self.area
        _x, _y, _w, _h = source_rect = (0, 0) + self.texture.size
        x_off = _w / 2
        y_off = _h / 2
        if not self.points:
            self.points = [random_position(source_rect) for count in range(self.star_count)]
            instructions = [("fill", (source_rect, ), {"color" : self.background_color})]
            color_kwargs = {"color" : self.color}
            point_instructions = (("point", (position, ), color_kwargs) for position in self.points)
            renderer = pride.objects[self.sdl_window].renderer
            renderer.draw(self.texture.texture, itertools.chain(instructions, point_instructions))
        source_rect = source_rect#
        area = x - x_off, y - y_off, w + (2 * x_off), h + (2 * y_off)
        self.draw("copy", self.texture, source_rect, area, self.angle)
        self.angle += self.angle_change


class Star_Background(pride.gui.gui.Window):

    defaults = {"star_count" : 0, "background_color" : (0, 0, 0, 255), "theme_type" : Star_Theme,
                "color" : (255, 255, 255, 240), "points" : tuple(), "_counter" : 4,
                "animate" : False}
    predefaults = {"_stars_drawn" : False, "_counter" : 0, "_pack_scheduled_value" : False}

    def _get__pack_scheduled(self): # using __pack_scheduled would mangle the name
        return self._pack_scheduled_value
    def _set__pack_scheduled(self, value):
        if self._pack_scheduled_value and not value:
            self._update_stars()
        self._pack_scheduled_value = value
    _pack_scheduled = property(_get__pack_scheduled, _set__pack_scheduled)

    def __init__(self, **kwargs):
        super(Star_Background, self).__init__(**kwargs)
        window = pride.objects[self.sdl_window]
        window.schedule_predraw_operation(self._update_stars)
        _max = max(window.size)
        self.texture = window.create_texture((_max, _max))

    def _update_stars(self):
        window = pride.objects[self.sdl_window]
        if self.animate:
            window.schedule_postdraw_operation(self._update_stars)
            self.texture_invalid = True
        _max = max(self.texture.size)
        w, h = self.size
        if _max < max(w, h):
            self.texture = window.create_texture((_max, _max))
            self.points = tuple()

def test():
    import pride.gui
    window = pride.objects[pride.gui.enable()]
    window.create(Star_Background, star_count=256)



if __name__ == "__main__":
    test()

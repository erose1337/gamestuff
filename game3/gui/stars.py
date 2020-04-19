#put rotating stars (points) in background
import itertools
import random

import pride.gui.gui
import pride.gui.color
import pride.gui.themes

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

COLORS = [pride.gui.color.Color(*[random.randint(0, 255) for x in range(4)]) for
          count in range(8)] + [pride.gui.color.Color(255, 255, 255, 255)] * 16
#TAILS = [random.randint(0, 6) for x in range(4)] + ([0] * 8)
TAILS = []
for x in range(5):
    TAILS.extend([5 - x] * x)

def random_color(colors=COLORS):
    return random.sample(colors, 1)[0]

def random_tail(tails=TAILS):
    return random.sample(tails, 1)[0]

class Star_Theme(pride.gui.themes.Theme):

    #theme_profiles = pride.gui.themes.Theme.copy()
    defaults = {"angle" : 10.0, "angle_change" : -.05}

    def draw_texture(self):
        x, y, w, h = area = self.area
        _x, _y, _w, _h = source_rect = (0, 0) + self.texture.size
        x_off = _w / 2
        y_off = _h / 2
        if not self.points:
            self.points = [random_position(source_rect) for count in range(self.star_count)]
            instructions = [("fill", (source_rect, ), {"color" : self.background_color})]
            point_instructions = []
            tails = []
            for position in self.points:
                _color = random_color()
                _color.a = random.randint(16, 255)
                color_kwargs = {"color" : _color}
                point_instructions.append(("point", (position, ), color_kwargs))

                glow_thickness = random.sample(([0] * 64) + ([1] * 4) + [2], 1)[0]
                if glow_thickness:
                    r, g, b, a = _color
                    fade_scalar = a / float(glow_thickness)
                    assert fade_scalar > 0
                    for thickness in range(glow_thickness):
                        instructions.append(("rect", ((position[0] - thickness, position[1] - thickness,
                                                      (3 * thickness), (3 * thickness)), ),
                                           dict(color=(r, g, b, a - int(thickness * fade_scalar)))))
            renderer = self.sdl_window.renderer
            renderer.draw(self.texture.texture, itertools.chain(instructions, point_instructions))

        source_rect = source_rect#
        area = x - x_off, y - y_off, w + (2 * x_off), h + (2 * y_off)
        self.draw("copy", self.texture, source_rect, area, self.angle)
        self.angle += self.angle_change

        #if not self.shooting_stars:
        #    stars = self.shooting_stars = []
        #    for count in range(random.randint(4, 128)):
        #        point1 = random_position(source_rect)
        #        direction = random.randint(-4, 4), random.randint(-4, 4)
        #        x2 = point1[0] + direction[0]
        #        y2 = point1[1] + direction[1]
        #        if x2 > _w:# point wraps around
        #            point1 = (0, point1[1])
        #        elif x2 < 0:
        #            point1 = (_w, point1[1])

        #        if y2 > _h:
        #            point1 = (point1[0], 0)
        #        elif y2 < 0:
        #            point1 = (point1[0], _h)
        #        point2 = (x2, y2)
        #        stars.append((point1, point2, direction))
        #else:
        #    new_stars = []
        #    for point1, point2, direction in self.shooting_stars:
        #        self.draw("line", point1 + point2, color=(255, 255, 55, 255))
        #        x3 = point2[0] + direction[0]
        #        y3 = point2[1] + direction[1]
        #        if x3 > _w :#or x3 < 0: # point wraps around
        #            print("next x too high ({})".format(x3))
        #            point2 = (0, point2[1])
        #        elif x3 < 0:
        #            print("next x too low ({})".format(x3))
        #            point2 = (_w, point2[1])
        #            #x3 = x3 % _w#point2[0] - (direction[0] * 2)
        #            #direction = (-direction[0], direction[1])
        #        if y3 > _h:# or y3 < 0:
        #            print("next y too high ({})".format(y3))
        #            point2 = (point2[0], 0)
        #        elif y3 < 0:
        #            print("next y too low ({})".format(y3))
        #            point2 = (point2[0], _h)
        #            #y3 = y3 % _h#point2[1] - (direction[0] * 2)
        #            #direction = (direction[0], -direction[1])
        #        point3 = (x3 % _w, y3 % _h)
        #        print point2, direction, point3
        #        raw_input()
        #        new_stars.append((point2, point3, direction))
        #    self.shooting_stars[:] = new_stars
        #if random.randint(1, 100) > 90:
        #    (position, direction,
        #     color, life) = [(random.randint(0, w), random.randint(0, h)),
        #                     random.sample(range(-40, 40), 2)[:2],
        #                     [random.randint(0, 255) for count in range(4)],
        #                     random.randint(4, 32)]
        #    self.shooting_stars.append((position, direction, color, life))
        #    self.draw("rect", (position[0] - 1, position[1] - 1, 3, 3), (255, 0, 0, 255))

        #remove = []
        #for position, direction, color, life in self.shooting_stars:
        #    new_position = position[0] + direction[0], position[1] + direction[1]
        #    print("Drawing at {} {}".format(new_position, color))
        #    self.draw("point", new_position, color=color)
        #    self.draw("rect", (new_position[0] - 1, new_position[1] - 1, 3, 3), (255, 255, 255, 255))
        #    life -= 1
        #    if not life:
        #        remove.append((position, direction, color, life))
        #for removal in remove:
        #    self.shooting_stars.remove(removal)


class Star_Background(pride.gui.gui.Window):

    defaults = {"star_count" : 0, "background_color" : (0, 0, 0, 255), "theme_type" : Star_Theme,
                "color" : (255, 255, 255, 240), "points" : tuple(), "_counter" : 4,
                "animate" : False}
    predefaults = {"_stars_drawn" : False, "_counter" : 0, "_pack_scheduled_value" : False}
    mutable_defaults = {"shooting_stars" : list}

    def _get__pack_scheduled(self): # using __pack_scheduled would mangle the name
        return self._pack_scheduled_value
    def _set__pack_scheduled(self, value):
        if self._pack_scheduled_value and not value:
            self._update_stars()
        self._pack_scheduled_value = value
    _pack_scheduled = property(_get__pack_scheduled, _set__pack_scheduled)

    def __init__(self, **kwargs):
        super(Star_Background, self).__init__(**kwargs)
        window = self.sdl_window
        window.schedule_predraw_operation(self._update_stars)
        _max = max(window.size)
        self.texture = window.create_texture((_max, _max), blendmode=sdl2.SDL_BLENDMODE_NONE)

    def _update_stars(self):
        window = self.sdl_window
        if self.animate:
            window.schedule_postdraw_operation(self._update_stars, self)
            self.texture_invalid = True
        _max = max(self.texture.size)
        w, h = self.size
        if _max < max(w, h):
            self.texture = window.create_texture((_max, _max), blendmode=sdl2.SDL_BLENDMODE_NONE)
            self.points = tuple()

def test():
    import pride.gui
    window = pride.objects[pride.gui.enable()]
    window.create(Star_Background, star_count=256)



if __name__ == "__main__":
    test()

# biome layer
# values between i ... j are considered a given type

# large elevation changes lead to deep wells

import copy
from math import log
from os import urandom

import pride.gui.gui
import pride.gui.themes

import sdl2

MOORE = [(-1,  1), (0, 1 ), (1, 1),
         (-1,  0),          (1, 0),
         (-1, -1), (0, -1), (1, -1)]

VONNEUMANN = [         (0, 1),
              (-1, 0),        (1, 0),
                       (0, -1)       ]

NEIGHBORHOOD = MOORE
N = 32
UP_ARROW = 1073741906
DOWN_ARROW = 1073741905
RIGHT_ARROW = 1073741903
LEFT_ARROW = 1073741904

class Biome_Data(object):

    def __init__(self, biome, water, light, elevation):
        self.biome = biome; self.water = water
        self.light = light; self.elevation = elevation


BIOME_MAPPING = dict((x, Biome_Data(x, 0, 255, 64)) for x in range(32))
BIOME_MAPPING.update(dict((x, Biome_Data(x, 64 + x, 255, 64)) for x in range(32, 64)))
BIOME_MAPPING.update(dict((x, Biome_Data(x, 0, 255, 64 + x)) for x in range(64, 96)))
BIOME_MAPPING.update(dict((x, Biome_Data(x, 32, 255, 32 + x)) for x in range(96, 256)))

class Place_Theme(pride.gui.themes.Minimal_Theme):

    def draw_texture(self):
        real_self = self.wrapped_object
        self.draw("set_blendmode", sdl2.SDL_BLENDMODE_BLEND)
        water = real_self.water; light = real_self.light
        elevation = real_self.elevation
        q = len(water); assert len(water[0]) == q;
        x_spacing = self.w / q; y_spacing = self.h / q
        for y in range(q):
            for x in range(q):
                self._draw_elevation(elevation, light, x, y, x_spacing, y_spacing)
                self._draw_water(water, light, x, y, x_spacing, y_spacing)
                #self._draw_light(light, x, y, x_spacing, y_spacing)
        self.draw("text", self.area, self.text,
                  width=self.w if self.wrap_text else None,
                  bg_color=self.text_background_color, color=self.text_color,
                  center_text=self.center_text, alias=self.font)

        self.update_state("water", elevation)
        if self.light_invalid:
            for count in range(5):
                self.update_state("light")
            real_self._current_light_frame += 3
            if real_self._current_light_frame >= real_self.light_frame_count:
                real_self.light_invalid = False
                real_self._current_light_frame = 0
        #pride.Instruction(self.sdl_window.reference, "schedule_postdraw_operation",
        #                  self._invalidate_texture, self).execute(priority=.025)
        self.sdl_window.schedule_postdraw_operation(self._invalidate_texture, self)
        self.draw("set_blendmode", pride.gui.sdllibrary.DRAW_BLENDMODE)

    def _draw_elevation(self, elevation, light, x, y, x_spacing, y_spacing):
        value = elevation[y][x]; lighting = max(0, light[y][x])
        if lighting and value:
            alpha = min(255, (value + lighting) / 2)
        else:
            alpha = 0
        if value <= 255:
            color = (180, 100, 25, alpha)
        else:
            magnitude = log(value, 2)
            r = min(255, magnitude * ((255 - 16) / 16))
            g = min(255, magnitude * ((255 - 15) / 16))
            b = min(255, magnitude * ((255 - 190) / 16))
            color = (r, g, b, alpha)
        self.draw("fill", (((x + self.window_x) * x_spacing) % self.w,
                           ((y + self.window_y) * y_spacing) % self.h,
                            x_spacing, y_spacing),
                  color=color)

    def _draw_water(self, water, light, x, y, x_spacing, y_spacing):
        value = water[y][x]; lighting = max(0, light[y][x])
        if lighting and value:
            alpha = min(255, (value + lighting) / 2)
        else:
            alpha = 0
        if value <= 255:
            color = (0, 40, 255, alpha)
        else:
            magnitude = log(value, 2)
            r = min(255, magnitude * (255 / 16))
            g = min(255, magnitude * ((255 - 40) / 16))
            color = (r, g, 255, alpha)
        self.draw("fill", (((x + self.window_x) * x_spacing) % self.w,
                           ((y + self.window_y) * y_spacing) % self.h,
                            x_spacing, y_spacing),
                  color=color)


class Place(pride.gui.gui.Window):

    defaults = {"pack_mode" : "top", "theme_type" : Place_Theme,
                "animation_enabled": False, "click_animation_enabled" : False,
                "neighborhood" : NEIGHBORHOOD, "water" : None,
                "elevation" : None, "light" : None, "dimension" : N,
                "matrix_names" : ("water", "elevation", "light", "null"),
                "current_target" : "water", "center_text" : False,
                "light_invalid" : True, "light_frame_count" : 5,
                "_current_light_frame" : 0, "window_x" : 0, "window_y" : 0,
                "topology" : "torus", "scroll_increment" : 1}
    hotkeys = {('1', None) : "set_to_water",
               ('2', None) : "set_to_elevation",
               ('3', None) : "set_to_light",
               (UP_ARROW, None) : "scroll_up",
               (DOWN_ARROW, None) : "scroll_down",
               (LEFT_ARROW, None) : "scroll_left",
               (RIGHT_ARROW, None) : "scroll_right"}
    mutable_defaults = {"biome_mapping" : lambda: BIOME_MAPPING}

    def __init__(self, **kwargs):
        super(Place, self).__init__(**kwargs)
        self.text = self.current_target
        n = self.dimension
        for matrix_name in self.matrix_names:
            matrix = getattr(self, matrix_name, None)
            if matrix is None:
                setattr(self, matrix_name, [[0] * n for x in range(n)])
            else:
                if not all(len(matrix) == len(row) for row in matrix):
                    raise ValueError("'{}' matrix is not square".format(matrix_name))
        #self.water = [[128] * n for x in range(n)]
        #self.light = [range(32) for x in range(n)]
        #self.elevation = [[128] * n for x in range(n)]
        self.biome = [range(16, 16 + n) for x in range(n)]
        for count in range(n):
            self.biome[ord(urandom(1)) % n][ord(urandom(1)) % n] = ord(urandom(1))
            self.update_state("biome")
        self.setup_biome()
        self.sdl_window.schedule_postdraw_operation(self._invalidate_texture, self)

    def setup_biome(self):
        biome_mapping = self.biome_mapping
        matrix = self.biome; water = self.water
        light = self.light; elevation = self.elevation
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                biome_data = biome_mapping[value]
                water[y][x] = biome_data.water
                light[y][x] = biome_data.light
                elevation[y][x] = biome_data.elevation

    def set_to_water(self):
        self.text = self.current_target = "water"

    def set_to_elevation(self):
        self.text = self.current_target = "elevation"

    def set_to_light(self):
        self.text = self.current_target = "light"

    def mousemotion(self, mouse_x, mouse_y, x_change, y_change, mouse):
        super(Place, self).mousemotion(mouse_x, mouse_y, x_change, y_change, mouse)
        if self.held:
            self.paint_cell(mouse_x, mouse_y, mouse)
        else:
            x, y, w, h = self.area; mouse_pos = (mouse_x, mouse_y)
            top = (x, y, w, 20); bottom = (x, y + h - 20, w, 20)
            left = (x, y, 20, h); right = (x + w - 20, y, 20, h)
            if pride.gui.point_in_area(top, mouse_pos):
                self.scroll_up()
            elif pride.gui.point_in_area(bottom, mouse_pos):
                self.scroll_down()
            elif pride.gui.point_in_area(left, mouse_pos):
                self.scroll_left()
            elif pride.gui.point_in_area(right, mouse_pos):
                self.scroll_right()

    def scroll_right(self):
        self.window_x -= self.scroll_increment

    def scroll_left(self):
        self.window_x += self.scroll_increment

    def scroll_down(self):
        self.window_y -= self.scroll_increment

    def scroll_up(self):
        self.window_y += self.scroll_increment

    def paint_cell(self, mouse_x, mouse_y, mouse):
        target = self.current_target
        matrix = getattr(self, target); q = len(matrix)
        x = mouse_x - self.x
        y = mouse_y - self.y
        x_spacing = self.w / q; y_spacing = self.h / q
        x_cell = ((x / x_spacing) - self.window_x) % q
        y_cell = ((y / y_spacing) - self.window_y) % q
        if mouse.button == sdl2.SDL_BUTTON_LEFT:
            try:
                matrix[y_cell][x_cell] = matrix[y_cell][x_cell] + 256
            except IndexError: # mouse moved outside of self
                pass
        else:
            #assert mouse.button in (sdl2.SDL_BUTTON_RIGHT,
            #                        sdl2.SDL_BUTTON_X1), mouse.button
            try:
                matrix[y_cell][x_cell] = matrix[y_cell][x_cell] - 256
            except IndexError:
                pass
        if target == "light":
            self.light_invalid = True
            self._current_light_frame = 0

    def update_state(self, name, matrix2=None):
        n = self.dimension;
        output = [[0] * n for _ in range(n)]
        matrix1 = getattr(self, name)
        if matrix2 is None:
            matrix2 = tuple((0, ) * n for _ in range(n))
        _before = sum(sum(row) for row in matrix1)    # for sanity check at end
        for y in range(n):
            for x in range(n):
                self.convolve_neighborhood(matrix1, matrix2, output, x, y)

        _after = sum(sum(row) for row in matrix1)
        assert _before == _after, (_before, _after)
        setattr(self, name, output)

    def convolve_neighborhood(self, matrix, difference, output, x, y):
        output[y][x] += matrix[y][x]# avoids need to copy entire matrix up-front
        neighborhood = self.neighborhood; topology = self.topology
        k = len(matrix); n = len(matrix[0]);
        z = len(neighborhood)

        if topology == "plane":
            def edges(offsets, x=x, y=y):
                xt, yt = x + offsets[0], y + offsets[1]
                if xt < 0 or yt < 0 or xt >= n or yt >= k:
                    return False
                else:
                    return True
            neighborhood = filter(edges, neighborhood)

        for x_offset, y_offset in neighborhood:
            xt, yt = x + x_offset, y + y_offset
            if topology == "torus":
                xt %= n;
                yt %= k

            delta = matrix[yt][xt] / z
            if not delta:
                continue

            adjustment = difference[y][x] - difference[yt][xt]
            if adjustment >= delta: # cannot move more than there actually is
                continue
            delta = delta - adjustment
            assert delta >= 0

            delta = min(matrix[yt][xt] / z, delta)
            output[y][x] += delta
            output[yt][xt] -= delta

            #delta = matrix[y][x] / z
            #if not delta:
            #    continue
            #delta = delta - (ELEVATION[yt][xt] - ELEVATION[y][x])
            #output[y][x] -= delta
            #output[yt][xt] += delta

class Topdown_Place(Place):

    pass


class Sidescroll_Place(Place):
    # use an elevation vector instead of an elevation matrix
    # uses gravity
    pass



def test_Place():
    import pride.gui
    from pride.gui.main import Gui
    window = pride.objects[pride.gui.enable(y=60)]
                                       #window_flags=sdl2.SDL_WINDOW_BORDERLESS)]
    window.tip_bar.hide()
    window.create(Gui, startup_programs=(Topdown_Place, ),
                  user=pride.objects["/User"])


if __name__ == "__main__":
    #test_discrete_convolution()
    test_Place()

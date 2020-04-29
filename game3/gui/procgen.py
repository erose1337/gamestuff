# biome layer
# values between i ... j are considered a given type

# large elevation changes lead to deep wells

# only process an area larger than the window but smaller than the whole place


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
N = 81
UP_ARROW = 1073741906
DOWN_ARROW = 1073741905
RIGHT_ARROW = 1073741903
LEFT_ARROW = 1073741904

class Biome_Data(object):

    def __init__(self, biome, water, light, elevation):
        self.biome = biome; self.water = water
        self.light = light; self.elevation = elevation


BIOME_MAPPING = dict()

BIOME_MAPPING.update(dict((x, Biome_Data(x, 0, 255, x)) for x in range(64)))
BIOME_MAPPING.update(dict((x, Biome_Data(x, x, 255, x)) for x in range(64, 128)))
BIOME_MAPPING.update(dict((x, Biome_Data(x, 0, 255, 64 + x)) for x in range(128, 192)))
BIOME_MAPPING.update(dict((x, Biome_Data(x, x, 255, 64 + x)) for x in range(192, 256)))

class Place_Theme(pride.gui.themes.Minimal_Theme):

    def draw_texture(self):
        real_self = self.wrapped_object
        self.draw("set_blendmode", sdl2.SDL_BLENDMODE_BLEND)
        water = real_self.water; light = real_self.light
        elevation = real_self.elevation
        k = real_self.dimension
        x_spacing = self.w / k; y_spacing = self.h / k
        for y in range(k):
            for x in range(k):
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
        n = self.dimension
        xt = (x + self.window_x) % n
        yt = (y - self.window_y) % n
        assert len(elevation) == n, (len(elevation), n)
        assert len(elevation[0]) == n, (len(elevation[0]), n)
        value = elevation[yt][xt]; lighting = max(0, light[yt][xt])
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
        self.draw("fill", ((x * x_spacing) % self.w,
                           (y * y_spacing) % self.h,
                            x_spacing, y_spacing),
                  color=color)

    def _draw_water(self, water, light, x, y, x_spacing, y_spacing):
        n = self.dimension
        xt = (x + self.window_x) % n
        yt = (y - self.window_y) % n
        value = water[yt][xt]; lighting = max(0, light[yt][xt])
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
        self.draw("fill", ((x * x_spacing) % self.w,
                           (y * y_spacing) % self.h,
                            x_spacing, y_spacing),
                  color=color)


class Place(pride.gui.gui.Window):

    defaults = {"pack_mode" : "top", "theme_type" : Place_Theme,
                "animation_enabled": False, "click_animation_enabled" : False,
                "neighborhood" : NEIGHBORHOOD, "dimension" : N,
                "matrix_names" : ("biome", "water", "elevation",
                                  "light", "null"),
                "current_target" : "zoom", "center_text" : False,
                "light_invalid" : True, "light_frame_count" : 5,
                "_current_light_frame" : 0, "window_x" : 0, "window_y" : 0,
                "topology" : "torus", "scroll_increment" : 1,
                "snapto_onclick" : True, "zoom_level" : 0}
    hotkeys = {('1', None) : "set_to_water",
               ('2', None) : "set_to_elevation",
               ('3', None) : "set_to_light",
               ('4', None) : "set_to_zoom",
               (UP_ARROW, None) : "scroll_up",
               (DOWN_ARROW, None) : "scroll_down",
               (LEFT_ARROW, None) : "scroll_left",
               (RIGHT_ARROW, None) : "scroll_right"}
    mutable_defaults = {"biome_mapping" : lambda: BIOME_MAPPING,
                        "scale_data" : list}

    def _get_elevation(self):
        return self.scale_data[self.zoom_level]["elevation"]
    def _set_elevation(self, value):
        self.scale_data[self.zoom_level]["elevation"] = value
    elevation = property(_get_elevation, _set_elevation)

    def _get_water(self):
        return self.scale_data[self.zoom_level]["water"]
    def _set_water(self, value):
        self.scale_data[self.zoom_level]["water"] = value
    water = property(_get_water, _set_water)

    def _get_light(self):
        return self.scale_data[self.zoom_level]["light"]
    def _set_light(self, value):
        self.scale_data[self.zoom_level]["light"] = value
    light = property(_get_light, _set_light)

    def _get_biome(self):
        return self.scale_data[self.zoom_level]["biome"]
    def _set_biome(self, value):
        self.scale_data[self.zoom_level]["biome"] = value
    biome = property(_get_biome, _set_biome)

    def _get_null(self):
        return self.scale_data[self.zoom_level]["null"]
    def _set_null(self, value):
        self.scale_data[self.zoom_level]["null"] = value
    null = property(_get_null)

    def __init__(self, **kwargs):
        super(Place, self).__init__(**kwargs)
        self.text = self.current_target
        n = self.dimension
        if n not in (3 ** x for x in range(7)):
            raise ValueError("dimension must be a small power of 3 (called with {})".format(n))

        data = dict(); self.scale_data.append(data)
        for matrix_name in self.matrix_names:
            data[matrix_name] = [[0] * n for x in range(n)]

        self.sdl_window.schedule_postdraw_operation(self._invalidate_texture, self)
        self.setup_biome()

    def setup_biome(self):
        print("Setting up biome...")
        n = self.dimension
        self.biome = [range(n) for x in range(n)]
        for count in range(n):
            self.biome[ord(urandom(1)) % n][ord(urandom(1)) % n] = ord(urandom(1))
        self.update_state("biome")
        biome_mapping = self.biome_mapping
        matrix = self.biome; water = self.water
        light = self.light; elevation = self.elevation
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                submatrix = (row[x:x+3] for row in matrix[y:y+3])
                value = sum(sum(row) for row in submatrix) / 9
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

    def set_to_zoom(self):
        self.text = self.current_target = "zoom"

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
            if pride.gui.point_in_area(left, mouse_pos):
                self.scroll_left()
            elif pride.gui.point_in_area(right, mouse_pos):
                self.scroll_right()

    def zoom_in(self):
        zoom = self.zoom_level
        new_zoom = max(0, zoom - 1)
        if zoom == new_zoom:
            return
        self.zoom_level = new_zoom

        scale_data = self.scale_data
        data = scale_data[zoom]
        data2 = scale_data[new_zoom]
        for name in self.matrix_names:
            if name in ("null", "biome"):
                continue
            matrix = data[name]
            matrix2 = data2[name]
            length = len(matrix) / 3
            for y in range(length):
                for x in range(length):
                    adjustment = matrix[x][y]
                    submatrix = [row[3*x:(3 * x) + 3] for row in
                                 matrix2[3*y:(3*y)+3]]
                    assert sum(len(row) for row in submatrix) == 9, len(submatrix)
                    adjustment -= sum(sum(row) for row in submatrix) / 9
                    if not adjustment:
                        continue
                    adjustment, remainder = divmod(adjustment, 9)
                    if adjustment:
                        for row in matrix2[3*y:(3*y)+3]:
                            for i in range(3):
                                #print(x + i, len(row))
                                row[x + i] += adjustment
                    if remainder:
                        xt, yt = divmod(remainder, 3)
                        matrix2[y + yt][x + xt] += remainder

    def compress_matrix(self, matrix):
        length = len(matrix)
        output = []
        for y in range(0, length, 3):
            new_row = []
            for x in range(0, length, 3):
                submatrix = (row[x:x+3] for row in matrix[y:y+3])
                new_row.append(sum(sum(row) for row in submatrix) / 9)
            output.append(new_row)
        return output

    def fill_out(self, matrix):
        size = self.dimension
        row_count = len(matrix); row_length = len(matrix[0])
        extra = 0; sign = 1
        while row_count != size: # fill with new rows
            new = ([], [], [])
            bottom_rows = matrix[-3:]
            for x in range(0, row_length, 3):
                submatrix = (row[x:x+3] for row in bottom_rows)
                value = sum(sum(row) for row in submatrix) / 9
                sign = pow(-1, (value & 1) ^ ((value & 2) >> 1))
                value = (value + extra, ) * 3
                new[0].extend(value); new[1].extend(value); new[2].extend(value)
                extra += sign * 1
            matrix.extend(new)
            row_count = len(matrix)

        extra = 0
        for y in range(0, size, 3): # start at the upper right-most 3x3 cell
            for x in range(0, size - row_length, 3):
                submatrix = (row[-3:] for row in matrix[y:y+3])
                value = sum(sum(row) for row in submatrix) / 9
                sign = pow(-1, (value & 1) ^ ((value & 2) >> 1))
                extra += sign * 1
                for row in matrix[y:y+3]:
                    row.extend((value + extra, ) * 3)
        assert len(matrix) == size, (len(matrix[0]), size)
        assert len(matrix[0]) == size, (len(matrix[0]), size)
        assert all(len(row) == len(matrix[0]) for row in matrix)

    def zoom_out(self):
        zoom = self.zoom_level
        scale_data = self.scale_data

        data = scale_data[zoom]
        try:
            data2 = scale_data[zoom + 1]
        except IndexError:
            data2 = dict()
            scale_data.append(data2)

        for name in ("elevation", "water", "light"):#self.matrix_names:
            matrix = data[name]; assert matrix is not None
            new_matrix = self.compress_matrix(matrix)
            if name not in data2:
                self.fill_out(new_matrix)
                data2[name] = new_matrix
            else:
                length = len(new_matrix)
                matrix2 = data2[name]
                for i, row in enumerate(new_matrix):
                    matrix2[i][:length] = row
        self.zoom_level += 1

    def scroll_right(self):
        self.window_x += self.scroll_increment
        self.window_x %= self.dimension

    def scroll_left(self):
        self.window_x -= self.scroll_increment
        self.window_x %= self.dimension

    def scroll_down(self):
        self.window_y -= self.scroll_increment
        self.window_y %= self.dimension

    def scroll_up(self):
        self.window_y += self.scroll_increment
        self.window_y %= self.dimension

    def left_click(self, mouse):
        target = self.current_target
        if target == "zoom":
            self.zoom_in()
        elif self.snapto_onclick:
            n = self.dimension
            x = mouse.x - self.x
            y = mouse.y - self.y
            x_spacing = self.w / n; y_spacing = self.h / n
            x_cell = x / x_spacing
            y_cell = y / y_spacing
            self.center_on(x_cell, y_cell)

    def center_on(self, x_cell, y_cell):
        offset = self.dimension / 2
        self.window_x += x_cell - offset
        self.window_y -= y_cell + offset
        self.window_x %= self.dimension; self.window_y %= self.dimension

    def right_click(self, mouse):
        target = self.current_target
        if target == "zoom":
            self.zoom_out()

    def paint_cell(self, mouse_x, mouse_y, mouse):
        target = self.current_target
        if target == "zoom":
            return
        n = self.dimension
        x = mouse_x - self.x
        y = mouse_y - self.y
        x_spacing = self.w / n; y_spacing = self.h / n
        x_cell = ((x / x_spacing) + self.window_x) % n
        y_cell = ((y / y_spacing) - self.window_y) % n
        matrix = getattr(self, target);

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
        #_before = sum(sum(row) for row in matrix1)    # for sanity check at end
        for y in range(n):
            for x in range(n):
                self.convolve_neighborhood(matrix1, matrix2, output, x, y)

        #_after = sum(sum(row) for row in matrix1)
        #assert _before == _after, (_before, _after)
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

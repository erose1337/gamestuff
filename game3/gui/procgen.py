# to do: add permeability
# the magnitude of the cell changes the amount of influx/outflux
# the difference between the magnitudes of the interacting cells changes the amount of influx/outflux


import copy
from math import log

import pride.gui.gui
import pride.gui.themes

import sdl2

# MOORE tends to keep changing and not settle to a final uniform state
MOORE = [(-1,  1), (0, 1 ), (1, 1),
         (-1,  0),          (1, 0),
         (-1, -1), (0, -1), (1, -1)]
# VONNEUMANN tends to settle to a final uniform state and not change anymore
VONNEUMANN = [         (0, 1),
              (-1, 0),        (1, 0),
                       (0, -1)       ]
GAUSSIAN = [(-1,  1), (0,  1), (1,  1),
            (-1,  0), (0,  0), (1,  0),
            (-1, -1), (0, -1), (1, -1)]

NEIGHBORHOOD = MOORE

def discrete_convolution(matrix, neighborhood=NEIGHBORHOOD):
    #assert all(len(row) == len(matrix[0]) for row in matrix)
    _before = sum(sum(row) for row in matrix)          # for sanity check at end

    output = copy.deepcopy(matrix)#[[0] * len(matrix[0]) for row_no in range(len(matrix))]
    for y, row in enumerate(matrix):
        for x, k in enumerate(row):
            convolve_neighborhood(matrix, output, x, y, neighborhood)
            #gaussian_kernel(matrix, output, x, y)

    _after = sum(sum(row) for row in output)
    assert _before == _after, (_before, _after)
    return output

def convolve_neighborhood(matrix, output, x, y, neighborhood=NEIGHBORHOOD):
    k = len(matrix); n = len(matrix[0]); z = len(neighborhood)
    for x_offset, y_offset in neighborhood:
        #xt, yt = (x + x_offset) % n, (y + y_offset) % k
        #delta = matrix[yt][xt] / z
        xt, yt = x + x_offset, y + y_offset
        if xt < 0 or yt < 0:
            continue
        try:
            delta = matrix[yt][xt] / z
        except IndexError:
            continue
        output[y][x] += delta
        output[yt][xt] -= delta

        delta = matrix[y][x] / z
        output[y][x] -= delta
        output[yt][xt] += delta

        #assert 0 <= output[yt][xt]
        #assert 0 <= output[y][x]

def gaussian_kernel(matrix, output, x, y, neighborhood=GAUSSIAN):
    q = len(matrix); z = 1656
    scalars =  iter([  19,  139,  19,
                      139, 1024, 139,
                       19,  139,  19])
    #scalars = iter([696389408,       113340712816370,      696389408,
    #                113340712816370, 18446744073709551616, 113340712816370,
    #                696389408,       113340712816370,      696389408])
    #z = 18447197439346374728

    for x_offset, y_offset in neighborhood:
        xt, yt = (x + x_offset) % q, (y + y_offset) % q
        output[yt][xt] += (matrix[y][x] * next(scalars)) / z
    #output[y][x] += 828
    #output[y][x] /= z


class Effect_Theme(pride.gui.themes.Minimal_Theme):

    def draw_texture(self):
        matrix = self.wrapped_object.matrix
        q = len(matrix); assert len(matrix[0]) == q;
        x_spacing = self.w / q; y_spacing = self.h / q
        for y, row in enumerate(matrix):
            for x, entry in enumerate(row):
                #color = tuple(matrix[y][x] for count in range(4))
                alpha = matrix[y][x]
                if alpha <= 255:
                    color = (80, 128, 255, alpha)
                else:
                    magnitude = log(alpha, 2)
                    r = min(255, magnitude * ((255 - 80) / 16))
                    g = min(255, magnitude * ((255 - 128) / 16))
                    color = (r, g, 255, 255)
                self.draw("fill", (x * x_spacing, y * y_spacing,
                                   x_spacing, y_spacing),
                          color=color)
        self.wrapped_object.matrix = discrete_convolution(matrix)
        #print_state(self.matrix)
        #raw_input()
        pride.Instruction(self.sdl_window.reference, "schedule_postdraw_operation",
                          self._invalidate_texture, self).execute(priority=.025)
        #self.sdl_window.schedule_postdraw_operation(self._invalidate_texture, self)
        #raw_input()

from os import urandom

class Effect(pride.gui.gui.Window):

    defaults = {"pack_mode" : "top", "theme_type" : Effect_Theme,
                "animation_enabled": False, "click_animation_enabled" : False}

    def matrix_callable():
        #import _matrix
        #return _matrix.matrix
        from os import urandom
        n = 64
        #_matrix = [range(i * 8, (i * 8) + n) for i in range(n)]
        _matrix = [[0] * n for x in range(n)]
        #for byte in urandom(256):
        #    _matrix[ord(byte) % n][ord(urandom(1)) % n] = 2 ** 10
        _matrix[11] = [255] * n
        _matrix[12] = [255] * n
        _matrix[13] = [255] * n
        center = n / 2
        #_matrix[center][center] = 2 ** 16
        return _matrix
        #return [range(32) + range(256 - 32, 256) for count in range(64)]
    mutable_defaults = {"matrix" : matrix_callable}

    def mousemotion(self, mouse_x, mouse_y, x_change, y_change, mouse):
        super(Effect, self).mousemotion(mouse_x, mouse_y, x_change, y_change, mouse)
        if not self.held:
            return
        matrix = self.matrix; q = len(matrix)
        x, y = mouse_x - self.x, mouse_y - self.y
        x_spacing = self.w / q; y_spacing = self.h / q
        x_cell = x / x_spacing
        y_cell = y / y_spacing
        if mouse.button == sdl2.SDL_BUTTON_LEFT:
            try:
                matrix[y_cell][x_cell] = matrix[y_cell][x_cell] + 65536
            except IndexError: # mouse moved outside of self
                pass
        else:
            assert mouse.button in (sdl2.SDL_BUTTON_RIGHT,
                                    sdl2.SDL_BUTTON_X1), mouse.button
            try:
                matrix[y_cell][x_cell] = max(0, matrix[y_cell][x_cell] - 65536)
            except IndexError:
                pass


def print_state(matrix):
    print '\n'.join(str(row).replace(", ", " ") for row in matrix)

def test_discrete_convolution():
    from pride.functions.utilities import slide
    m = [[1, 0, 0, 0, 0],
         [1, 8, 0, 0, 0],
         [0, 0, 64, 0, 0],
         [0, 0, 0, 64, 0],
         [0, 0, 0, 0, 0]]
    #m = [chunk for chunk in slide(range(25), 5)]
    #from os import urandom
    #m = [list(bytearray(urandom(5))) for chunk in range(5)]
    print_state(m)
    while True:
        m = discrete_convolution(m)
        print
        print_state(m)
        raw_input()

def test_Effect():
    import pride.gui
    from pride.gui.main import Gui
    window = pride.objects[pride.gui.enable(y=60)]
                                       #window_flags=sdl2.SDL_WINDOW_BORDERLESS)]
    window.tip_bar.hide()
    window.create(Gui, startup_programs=(Effect, ), user=pride.objects["/User"])


if __name__ == "__main__":
    #test_discrete_convolution()
    test_Effect()

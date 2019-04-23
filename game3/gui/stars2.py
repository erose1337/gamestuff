# replace
#   x = self.create(y).reference
# with a descriptor
#   return pride.objects[self.__y_ref]
#
#   set self.__y_ref = value
import pride.gui.gui

import sdl2.sdlgfx

class Star_Background(pride.gui.gui.Window):

    defaults = {"smoothing" : sdl2.sdlgfx.SMOOTHING_OFF
    allowed_values = {"smoothing" : (sdl2.sdlgfx.SMOOTHING_OFF, sdl2.sdlgfx.SMOOTHING_ON)}

    def __init__(self, **kwargs):
        super(Star_Background, self).__init__(**kwargs)
        sprite = self.renderer.sprite_factory.create_software_sprite(size)
        self.sprite = sprite
        surface = sprite.surface
        window = pride.objects[self.sdl_window]
        renderer = window.renderer

        for point in self.points:
            # draw point in sprite
            renderer.set_render_target(surface)
            renderer.draw(surface, operations)

        # every x frames, rotozoom the sprite
        window.schedule_predraw_operation(self.rotozoom_sprite)

    def rotozoom_sprite(self):
        #def rotozoom(surface, angle, zoom, smooth):
        sdl2.sdlgfx.rotozoomSurface(self.sprite.surface, 10.0, 1.0, self.smoothing)

    def draw_texture(self):
        super(Star_Background, self).draw_texture()
        self.draw("copy", self.sprite.surface, dstrect=self.area)

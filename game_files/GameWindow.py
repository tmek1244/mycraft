import math

from pyglet.gl import *
from pyglet.window import FPSDisplay, key

from Settings import Settings
from model import Model
from player import Player


class GameWindow(pyglet.window.Window):

    @staticmethod
    def push(pos, rot):
        glPushMatrix()
        glRotatef(-rot[1], 1, 0, 0)
        glRotatef(-rot[0], 0, 1, 0)
        glTranslatef(-pos[0], -pos[1], -pos[2], )

    @staticmethod
    def my_projection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

    @staticmethod
    def model_function():
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set2d(self):
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, float(self.width), 0, float(self.height), -1, 1)
        self.model_function()

    def set3d(self):
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

        self.my_projection()
        gluPerspective(70, self.width / self.height, 0.05, 1000)
        self.model_function()

    def set_lock(self, state):
        self.lock = state
        self.set_exclusive_mouse(state)

    lock = False
    mouse_lock = property(lambda self: self.lock, set_lock)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = Settings()['game_window']

        self.set_minimum_size(self.settings['min_size_x'], self.settings['min_size_y'])
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.how_far = self.settings['chunks']
        self.fps_display = FPSDisplay(self)
        # self.fps_display.label.y = self.height - 50
        # self.fps_display.label.x = self.width - 150
        self.cross = pyglet.image.load('images/cross.png')
        self.label = pyglet.text.Label("",
                                       font_name='Times New Roman',
                                       font_size=18,
                                       x=self.width // 2, y=40,
                                       anchor_x='center', anchor_y='center')

        self.model = Model()
        self.y = 0
        position = self.settings['player_start_position']
        player_start_coords = (position['x'], position['y'], position['z'])
        player_start_rotation = (position['rot_x'], position['rot_y'])
        self.player = Player(self.model, player_start_coords, player_start_rotation)

    def on_mouse_press(self, x, y, button, modifiers):
        self.player.mouse_press(button)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_lock:
            self.player.mouse_motion(dx, dy)

    def on_key_press(self, user_key, mod):
        if user_key == key.ESCAPE:
            self.close()
        elif user_key == key.E:
            self.mouse_lock = not self.mouse_lock

    def update(self, dt):
        # print(self.player.pos[1])
        self.player.update(dt, self.keys)

    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos, self.player.rot)
        x = math.floor(self.player.pos[0] / Settings.get_chunk_size())
        z = math.floor(self.player.pos[2] / Settings.get_chunk_size())
        # _thread.start_new_thread(self.model.draw, (x, z, self.how_far, (self.player.rot[0] + 180) % 360, ))
        self.model.draw(x, z, self.how_far, (self.player.rot[0] + 180) % 360)
        glPopMatrix()
        self.fps_display.draw()
        self.set2d()

        self.label.text = self.player.eq.print_content()
        self.label.draw()

        self.cross.blit(self.width // 2 - 20, self.height // 2 - 20)

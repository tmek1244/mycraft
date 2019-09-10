from pyglet import clock
from pyglet.gl import *
from pyglet.window import key
from pyglet import image
import math

from player import Player
from model import Model


class Window(pyglet.window.Window):

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
        self.Projection()
        gluOrtho2D(0, self.width, 0, self.height)
        self.model_function()

    def set3d(self):
        self.my_projection()
        gluPerspective(70, self.width / self.height, 0.05, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.model_function()

    def set_lock(self, state):
        self.lock = state
        self.set_exclusive_mouse(state)

    lock = False
    mouse_lock = property(lambda self: self.lock, set_lock)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model()
        self.y = 0
        self.player = Player(self.model, (10, 45, 10), (0, 0))

        self.label = pyglet.text.Label('Hello, world',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x=self.width // 2,
                                       y=self.height // 2,
                                       anchor_x='center', anchor_y='center')

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
        x = math.floor(self.player.pos[0] / 16)
        z = math.floor(self.player.pos[2] / 16)
        how_far = 5

        # print(clock.get_fps())

        self.model.draw(x, z, how_far, (self.player.rot[0] + 180) % 360)

        glPopMatrix()
        self.set2d()
        self.label.draw()


if __name__ == '__main__':
    window = Window(width=854, height=480, caption='Minecraft', resizable=True)
    glClearColor(0.5, 0.7, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    pyglet.app.run()

from pyglet import clock
from pyglet.gl import *
from pyglet.window import key, FPSDisplay
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
        self.set_minimum_size(300, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.how_far = 5
        self.fps_display = FPSDisplay(self)
        # self.fps_display.label.y = self.height - 50
        # self.fps_display.label.x = self.width - 150
        self.cross = pyglet.image.load('cross.png')

        self.model = Model()
        self.y = 0
        self.player = Player(self.model, (0.5, 45, 0.5), (0, 0))

        self.label = pyglet.text.Label('Hello, world',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x= 300,  # self.width // 2,
                                       y= 300)  # self.height // 2,
                                       # anchor_x='center', anchor_y='center')

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
        self.model.draw(x, z, self.how_far, (self.player.rot[0] + 180) % 360)
        glPopMatrix()
        self.fps_display.draw()
        self.set2d()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.cross.blit(self.width//2 - 20, self.height//2 - 20)
        # self.label.draw()


if __name__ == '__main__':
    window = Window(width=854, height=480, caption='Minecraft', resizable=True)
    glClearColor(0.5, 0.7, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    pyglet.app.run()

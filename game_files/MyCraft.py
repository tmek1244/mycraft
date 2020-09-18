from pyglet.gl import *


from game_files.GameWindow import GameWindow


def my_craft():
    window = GameWindow(width=854, height=480, caption='Minecraft', resizable=True)
    glClearColor(0.5, 0.7, 1, 1)
    glEnable(GL_DEPTH_TEST)
    # glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    pyglet.app.run()

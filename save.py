from pyglet.gl import *

import numpy as np
import noise
import random


def get_tex(file):
    tex = pyglet.image.load(file).get_texture()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return pyglet.graphics.TextureGroup(tex)


def what_side_add(world, x, y, z, char):
    return char if world[x, y, z] == 0 else ""


class ChunkSave:
    WIDTH = 16
    LENGTH = 16
    HEIGHT = 50
    OFFSET = 0.02
    HEIGHT_OF_TERRAIN = 30

    def __init__(self, pos_x, pos_z):
        self.textures = get_tex('textures.png')
        self.previous_block_type = 0
        self.is_draw = False
        self.pos_x = pos_x * self.WIDTH
        self.pos_z = pos_z * self.LENGTH
        self.batch = pyglet.graphics.Batch()

        self.world = np.zeros((self.WIDTH + 2, self.HEIGHT, self.LENGTH + 2))
        self.vertex_list = {}

        self.top_texture = ((0, 7/8, 1/8, 7/8, 1/8, 1, 0, 1),  # grass_top
                            (2/8, 7/8, 3/8, 7/8, 3/8, 1, 2/8, 1),  # dirt
                            (3/8, 7/8, 4/8, 7/8, 4/8, 1, 3/8, 1),  # stone
                            (4/8, 7/8, 5/8, 7/8, 5/8, 1, 4/8, 1),  # sand
                            (7/8, 7/8, 1, 7/8, 1, 1, 7/8, 1))  # wood_top
        self.side_texture = ((1/8, 7/8, 2/8, 7/8, 2/8, 1, 1/8, 1),  # grass_side
                             (2/8, 7/8, 3/8, 7/8, 3/8, 1, 2/8, 1),  # dirt
                             (3/8, 7/8, 4/8, 7/8, 4/8, 1, 3/8, 1),  # stone
                             (4/8, 7/8, 5/8, 7/8, 5/8, 1, 4/8, 1),  # sand
                             (5/8, 7/8, 6/8, 7/8, 6/8, 1, 5/8, 1))  # wood_side
        self.bottom_texture = ((2/8, 7/8, 3/8, 7/8, 3/8, 1, 2/8, 1),  # dirt
                               (2/8, 7/8, 3/8, 7/8, 3/8, 1, 2/8, 1),  # dirt
                               (3/8, 7/8, 4/8, 7/8, 4/8, 1, 3/8, 1),  # stone
                               (4/8, 7/8, 5/8, 7/8, 5/8, 1, 4/8, 1),  # sand
                               (7/8, 7/8, 1, 7/8, 1, 1, 7/8, 1))  # wood_top

        self.create_chunk()

    def create_chunk(self):
        self.fill_arrays()
        # self.add_trees()
        self.generate_chunk()

    def fill_arrays(self):
        x_off = self.pos_x * self.OFFSET
        for x in range(-1, self.WIDTH + 1):
            z_off = self.pos_z * self.OFFSET
            for z in range(-1, self.LENGTH + 1):
                high = self.HEIGHT_OF_TERRAIN * np.abs(noise.pnoise2(x_off, z_off)) + \
                       (self.HEIGHT - self.HEIGHT_OF_TERRAIN)
                # high = 30
                for y in range(2, int(high)):
                    if y < int(high) - 2:
                        self.world[x, y, z] = 3
                    else:
                        self.world[x, y, z] = 2
                self.world[x, int(high), z] = 1

                z_off += self.OFFSET

            x_off += self.OFFSET

    def add_trees(self):
        for x in range(0, self.WIDTH):
            for z in range(0, self.LENGTH):
                if random.random() < 0.01:
                    y = self.return_height(x, self.HEIGHT - 1, z)
                    # self.world[x, y, z] = 2
                    # self.world[x, y + 1, z] = 2
                    # self.world[x, y + 2, z] = 2
                    self.world[x, y + 3, z] = 2

    def where_add_block(self, x, y, z):
        where = ""
        where += what_side_add(self.world, x, y + 1, z, "t")  # top
        where += what_side_add(self.world, x, y - 1, z, "d")  # down

        where += what_side_add(self.world, x, y, z - 1, "b")  # back
        where += what_side_add(self.world, x, y, z + 1, "f")  # front

        where += what_side_add(self.world, x + 1, y, z, "r")  # right
        where += what_side_add(self.world, x - 1, y, z, "l")  # left

        return where

    def generate_chunk(self):
        for x in range(0, self.WIDTH):
            for z in range(0, self.LENGTH):
                for y in range(self.HEIGHT - self.HEIGHT_OF_TERRAIN - 1, self.HEIGHT):
                    if self.world[x, y, z] != 0:
                        where = self.where_add_block(x, y, z)
                        self.add_block(x, y, z, where, self.world[x, y, z])
                        # self.delete_from_batch(x, y, z, "t")

    def add_block(self, x, y, z, where, block_type):
        if "a" in where:
            self.world[x, y, z] = block_type
        if self.previous_block_type != block_type:
            # self.set_texture(int(block_type))
            self.previous_block_type = block_type
        if "b" in where:
            self.vertex_list[(x, y, z, "b")] = self.add_to_batch(x, y, z, "back", block_type)
        if "f" in where:
            self.vertex_list[(x, y, z, "f")] = self.add_to_batch(x, y, z, "front", block_type)

        if "l" in where:
            self.vertex_list[(x, y, z, "l")] = self.add_to_batch(x, y, z, "left", block_type)
        if "r" in where:
            self.vertex_list[(x, y, z, "r")] = self.add_to_batch(x, y, z, "right", block_type)

        if "d" in where:
            self.vertex_list[(x, y, z, "d")] = self.add_to_batch(x, y, z, "down", block_type)
        if "t" in where:
            self.vertex_list[(x, y, z, "t")] = self.add_to_batch(x, y, z, "top", block_type)

    def add_to_batch(self, x, y, z, where, block_type):
        tex_coords = ('t2f', (0, 7/8, 1/8, 7/8, 1/8, 1, 0, 1))
        x += self.pos_x
        z += self.pos_z
        X, Y, Z = x + 1, y + 1, z + 1

        switcher = {
            "back": ((X, y, z, x, y, z, x, Y, z, X, Y, z), "s"),
            "front": ((x, y, Z, X, y, Z, X, Y, Z, x, Y, Z), "s"),

            "left": ((x, y, z, x, y, Z, x, Y, Z, x, Y, z), "s"),
            "right": ((X, y, Z, X, y, z, X, Y, z, X, Y, Z), "s"),

            "down": ((x, y, z, X, y, z, X, y, Z, x, y, Z), "b"),
            "top": ((x, Y, Z, X, Y, Z, X, Y, z, x, Y, z), "t")
        }
        block_type = int(block_type)
        print(block_type)
        if switcher.get(where)[1] == "s":
            tex_coords = self.side_texture[block_type - 1]
        elif switcher.get(where)[1] == "b":
            tex_coords = self.bottom_texture[block_type - 1]
        else:
            tex_coords = self.top_texture[block_type - 1]
        coords = switcher.get(where)[0]
        return self.batch.add(4, GL_QUADS, self.textures, ('v3f', coords), ('t2f', tex_coords))

    def return_height(self, x, y, z):
        while self.world[x, y, z] == 0:
            y -= 1
        return y

    def draw(self):
        self.batch.draw()

    def delete_from_batch(self, x, y, z, where="bflrdtu"):
        # y -= 1
        # print(self.vertex_list)
        # print(x, y, z)
        for letter in "bflrdt":
            if (x, y, z, letter) in self.vertex_list:
                # print(x, y, z, letter)
                if (x, y, z, letter) in self.vertex_list:
                    self.vertex_list[(x, y, z, letter)].delete()
                del self.vertex_list[(x, y, z, letter)]
        if "u" in where:
            self.world[x, y, z] = 0
        if "f" in where:
            self.check_and_add(x, y, z - 1, "f")
        if "b" in where:
            self.check_and_add(x, y, z + 1, "b")

        if "r" in where:
            self.check_and_add(x - 1, y, z, "r")
        if "l" in where:
            self.check_and_add(x + 1, y, z, "l")

        if "t" in where:
            self.check_and_add(x, y - 1, z, "t")
        if "d" in where:
            self.check_and_add(x, y + 1, z, "d")

    def check_and_add(self, x, y, z, word):
        # print("dodano: ", word, " na pozycji: ", x, y, z)  # self.world[x, y, z])e
        if self.world[x, y, z] != 0:
            self.add_block(x, y, z, word, self.world[x, y, z])

    def return_world(self, x, y, z):
        try:
            return self.world[x, y, z]
        except IndexError:
            return -10

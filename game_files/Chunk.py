import numpy as np
import noise


from pyglet.gl import *

from game_files.Settings import Settings
from biomes import meadowBiome

TRANSPARENT_BLOCKS = (0, 8)


def get_tex(file):
    tex = pyglet.image.load(file).get_texture()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return pyglet.graphics.TextureGroup(tex)


def what_side_add(world, x, y, z, char):
    return char if world[x, y, z] in TRANSPARENT_BLOCKS else ""


def return_coordinate_of_texture(which_block):
    x = which_block % 8
    y = which_block // 8
    return (x/8, (7 - y)/8,
            (x + 1)/8, (7 - y)/8,
            (x + 1)/8, (8 - y)/8,
            x/8, (8 - y)/8)


class Chunk:
    WIDTH = Settings.get_chunk_size()
    LENGTH = Settings.get_chunk_size()
    HEIGHT = Settings.get_max_height()
    OFFSET = 0.02
    HEIGHT_OF_TERRAIN = Settings()['terrain_height']

    top_texture = ((0, 7 / 8, 1 / 8, 7 / 8, 1 / 8, 1, 0, 1),  # grass_top 1
                   (2 / 8, 7 / 8, 3 / 8, 7 / 8, 3 / 8, 1, 2 / 8, 1),  # dirt 2
                   (3 / 8, 7 / 8, 4 / 8, 7 / 8, 4 / 8, 1, 3 / 8, 1),  # stone 3
                   (4 / 8, 7 / 8, 5 / 8, 7 / 8, 5 / 8, 1, 4 / 8, 1),  # sand 4
                   (6 / 8, 7 / 8, 7 / 8, 7 / 8, 7 / 8, 1, 6 / 8, 1),  # wood_top 5
                   (7 / 8, 7 / 8, 8 / 8, 7 / 8, 8 / 8, 1, 7 / 8, 1))  # leaves 6
    side_texture = ((1 / 8, 7 / 8, 2 / 8, 7 / 8, 2 / 8, 1, 1 / 8, 1),  # grass_side
                    (2 / 8, 7 / 8, 3 / 8, 7 / 8, 3 / 8, 1, 2 / 8, 1),  # dirt
                    (3 / 8, 7 / 8, 4 / 8, 7 / 8, 4 / 8, 1, 3 / 8, 1),  # stone
                    (4 / 8, 7 / 8, 5 / 8, 7 / 8, 5 / 8, 1, 4 / 8, 1),  # sand
                    (5 / 8, 7 / 8, 6 / 8, 7 / 8, 6 / 8, 1, 5 / 8, 1),  # wood_side
                    (7 / 8, 7 / 8, 8 / 8, 7 / 8, 8 / 8, 1, 7 / 8, 1))  # leaves
    bottom_texture = ((2 / 8, 7 / 8, 3 / 8, 7 / 8, 3 / 8, 1, 2 / 8, 1),  # dirt
                      (2 / 8, 7 / 8, 3 / 8, 7 / 8, 3 / 8, 1, 2 / 8, 1),  # dirt
                      (3 / 8, 7 / 8, 4 / 8, 7 / 8, 4 / 8, 1, 3 / 8, 1),  # stone
                      (4 / 8, 7 / 8, 5 / 8, 7 / 8, 5 / 8, 1, 4 / 8, 1),  # sand
                      (6 / 8, 7 / 8, 7 / 8, 7 / 8, 7 / 8, 1, 6 / 8, 1),  # wood_top
                      (7 / 8, 7 / 8, 8 / 8, 7 / 8, 8 / 8, 1, 7 / 8, 1))  # leaves
    textures_top = get_tex('images/texturest.png')
    textures_side = get_tex('images/texturess.png')
    textures_bottom = get_tex('images/texturesb.png')

    def __init__(self, pos_x, pos_z):
        # self.previous_block_type = 0
        self.is_draw = False
        self.pos_x = pos_x * self.WIDTH
        self.pos_z = pos_z * self.LENGTH
        self.batch = pyglet.graphics.Batch()
        self.was_generated = False

        self.world = np.zeros((self.WIDTH + 2, self.HEIGHT, self.LENGTH + 2))
        self.vertex_list = {}

        self.min_height = self.HEIGHT
        self.max_height = 0

        self.fill_arrays()

    def fill_arrays(self):
        # time1 = time.time()
        x_off = self.pos_x * self.OFFSET
        for x in range(-1, self.WIDTH + 1):
            z_off = self.pos_z * self.OFFSET
            for z in range(-1, self.LENGTH + 1):
                height = self.HEIGHT_OF_TERRAIN * np.abs(noise.pnoise2(x_off, z_off)) + \
                       (self.HEIGHT - self.HEIGHT_OF_TERRAIN)
                # high = 30
                biome = noise.pnoise1(x_off * (z_off + x_off) / Settings.get_chunk_size())
                # if biome > -0.1:
                #     height = self.HEIGHT_OF_TERRAIN * np.abs(noise.pnoise2(x_off, z_off)) + \
                #            (self.HEIGHT - self.HEIGHT_OF_TERRAIN)
                #     # elevation = np.abs(noise.pnoise2(x_off, z_off))
                #     # roughness = np.abs(noise.pnoise2(x_off, z_off))
                #     # detail = np.abs(noise.pnoise2(x_off, z_off))
                #     # high = max((elevation + (roughness*detail)) * self.HEIGHT_OF_TERRAIN + (self.HEIGHT - self.HEIGHT_OF_TERRAIN), self.HEIGHT - 13)
                # else:
                #     height = self.HEIGHT_OF_TERRAIN * np.abs(noise.pnoise2(z_off, x_off)) + \
                #            (self.HEIGHT - self.HEIGHT_OF_TERRAIN)
                height = meadowBiome.MeadowBiome.add(self.world, x, z, self.pos_x, self.pos_z)
                if self.min_height > height:
                    self.min_height = height

                if self.max_height < height:
                    self.max_height = max(height, 140)
                # if 0 <= x < self.WIDTH and 0 <= z < self.LENGTH:
                # meadowBiome.MeadowBiome.add_meadow(self.world, x, z, self.pos_x, self.pos_z)
                # else:
                #     for y in range(2, height + 1):
                #         if y < height - 2:
                #             self.world[x, y, z] = 3
                #         elif biome > -0.1:
                #             if y < height:
                #                 self.world[x, y, z] = 2
                #             else:
                #                 self.world[x, y, z] = 1
                #         else:
                #             self.world[x, y, z] = 4
                z_off += self.OFFSET

            x_off += self.OFFSET
        # print(time.time() - time1)
        # print(self.min_height)

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
                for y in range(self.min_height - 1, self.max_height + 9):
                    if self.world[x, y, z] != 0:
                        where = self.where_add_block(x, y, z)
                        if where != "":
                            self.add_block(x, y, z, where, self.world[x, y, z])
                        # self.delete_from_batch(x, y, z, "t")

    def add_block(self, x, y, z, which_side, block_type):
        if "a" in which_side:
            self.world[x, y, z] = block_type
            which_side = which_side.replace("a", '')

        for i in which_side:
            self.add_to_vertex_list(x, y, z, i, block_type)

    def add_to_vertex_list(self, x, y, z, where, block_type):
        if (x, y, z, where) not in self.vertex_list:
            self.vertex_list[(x, y, z, where)] = self.add_to_batch(x, y, z, where, block_type)

    def add_to_batch(self, x, y, z, which_side, block_type):
        # tex_coords = ('t2f', (0, 7/8, 1/8, 7/8, 1/8, 1, 0, 1))
        x += self.pos_x
        z += self.pos_z

        X, Y, Z = x + 1, y + 1, z + 1

        switcher = {
            "b": ((X, y, z, x, y, z, x, Y, z, X, Y, z), "side"),
            "f": ((x, y, Z, X, y, Z, X, Y, Z, x, Y, Z), "side"),

            "l": ((x, y, z, x, y, Z, x, Y, Z, x, Y, z), "side"),
            "r": ((X, y, Z, X, y, z, X, Y, z, X, Y, Z), "side"),

            "d": ((x, y, z, X, y, z, X, y, Z, x, y, Z), "bottom"),
            "t": ((x, Y, Z, X, Y, Z, X, Y, z, x, Y, z), "top")
        }
        block_type = int(block_type)
        # print(block_type)
        if switcher.get(which_side)[1] == "side":
            textures = self.textures_side
        elif switcher.get(which_side)[1] == "bottom":
            textures = self.textures_bottom
        else:
            textures = self.textures_top
        coords = switcher.get(which_side)[0]
        tex_coords = return_coordinate_of_texture(block_type)
        return self.batch.add(4, GL_QUADS, textures, ('v3f', coords), ('t2f', tex_coords))

    def return_height(self, x, y, z):
        while self.world[x, y, z] == 0:
            y -= 1
        return y

    def draw(self):
        if not self.was_generated:
            self.generate_chunk()
            self.was_generated = True
        self.batch.draw()

    def delete_block_from_batch(self, x, y, z, which_side="bflrdtu"):
        # print(where)
        if "u" in which_side:
            self.world[x, y, z] = 0
        for letter in "bflrdt" if "u" in which_side else which_side:
            self.check_and_delete_sides(x, y, z, letter)

    def check_and_add_sides(self, x, y, z, which_side):
        if self.world[x, y, z] != 0:
            # print("check_and_add : ",x, y, z, word)
            # print(x, y, z, which_side)
            self.add_block(x, y, z, which_side, self.world[x, y, z])

    def check_and_delete_sides(self, x, y, z, which_side):
        if (x, y, z, which_side) in self.vertex_list:
            self.vertex_list[(x, y, z, which_side)].delete()
            del self.vertex_list[(x, y, z, which_side)]

    def return_world(self, x, y, z):
        try:
            return self.world[x, y, z]
        except IndexError:
            return -10

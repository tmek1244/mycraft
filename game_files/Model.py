import math
import random


from game_files.Chunk import Chunk
from game_files.Chunk import TRANSPARENT_BLOCKS
from game_files.Settings import Settings


def which_chunk(x, y):
    return math.floor(x / Settings.get_chunk_size()), math.floor(y / Settings.get_chunk_size())


def floor_for_coords(x, y, z):
    return math.floor(x), math.floor(y), math.floor(z)


def return_angle(x, y):
    if x == 0:
        return 90 if y > 0 else 270
    angle = math.degrees(math.atan(y / x)) if x > 0 else math.degrees(math.atan(y / x)) + 180
    return angle % 360


def side_manager(what_to_do, which_side, x, y, z):
    if "b" not in which_side:
        what_to_do(x, y, z - 1, "f")
    if "f" not in which_side:
        what_to_do(x, y, z + 1, "b")
    if "l" not in which_side:
        what_to_do(x - 1, y, z, "r")
    if "r" not in which_side:
        what_to_do(x + 1, y, z, "l")
    if "d" not in which_side:
        what_to_do(x, y - 1, z, "t")
    if "t" not in which_side:
        what_to_do(x, y + 1, z, "d")


class Model:
    PLAYER_SIZE = 0.2

    def __init__(self):
        self.dic_chunks = {}
        self.was_there_new = False
        self.fully_completed = []

    def draw(self, x, y, how_far, angle):
        self.was_there_new = False
        for k in range(0, how_far):
            for i, j in ((x, y) for x in range(-k, k + 1) for y in range(-k, k + 1) if abs(x) + abs(y) == k):
                if self.is_visible(angle, i, j) or k < 3:
                    if self.is_ready_to_drawing(x + i, y + j):
                        self.draw_chunk(x + i, y + j)

    def is_ready_to_drawing(self, x, y):
        if (x, y) in self.fully_completed:
            return True
        elif self.is_created(x, y) and not self.was_there_new:
            self.add_structures_to_chunk(x, y)
            self.fully_completed.append((x, y))
            self.was_there_new = True
        elif not self.was_there_new:
            self.add_new_chunk(x, y)
            self.add_structures_to_chunk(x, y)
            self.fully_completed.append((x, y))
            self.was_there_new = True
        return False

    def add_new_chunk(self, x, y):
        self.dic_chunks[(x, y)] = Chunk(x, y)

    def is_created(self, x, y):
        return (x, y) in self.dic_chunks

    def draw_chunk(self, x, y):
        self.dic_chunks[(x, y)].draw()

    def return_max_height(self, pos):
        max_height = 0
        for i in (-self.PLAYER_SIZE, 0, self.PLAYER_SIZE):
            for j in (-self.PLAYER_SIZE, 0, self.PLAYER_SIZE):
                max_height = max(max_height, self.return_height(pos[0] + i, pos[1], pos[2] + j))

        return max_height

    @staticmethod
    def is_visible(main_angle, x, y):
        angle = (-return_angle(x, y) + 90) % 360
        angle_of_sight = 90

        if main_angle > (360 - angle_of_sight):
            if main_angle - angle_of_sight <= angle <= 360 or angle <= (main_angle + angle_of_sight) % 360:
                return True
            else:
                return False
        if main_angle < angle_of_sight:
            if angle <= main_angle + angle_of_sight or angle >= (main_angle - angle_of_sight) % 360:
                return True
            else:
                return False
        if main_angle - angle_of_sight <= angle <= main_angle + angle_of_sight:
            return True
        else:
            return False

    def return_deleted_block(self, x, y, z):
        chunk_x, chunk_y = which_chunk(x, z)
        if self.return_world(x, y, z) == 0:
            return 0
        which_block = self.return_world(x, y, z)
        which_sides = self.where_add_side(x, y, z) + "u"
        side_manager(self.check_and_add_sides, which_sides, x, y, z)
        if self.is_created(chunk_x, chunk_y):
            self.delete_sides(x, y, z, which_sides)

        return which_block

    def add_block(self, x, y, z, block_type=3):
        x, y, z = floor_for_coords(x, y, z)
        chunk_x, chunk_y = which_chunk(x, z)
        # which_side = ""
        which_side = self.where_add_side(x, y, z) + "a"
        if block_type not in TRANSPARENT_BLOCKS:
            side_manager(self.check_and_delete_sides, which_side, x, y, z)

        self.dic_chunks[(chunk_x, chunk_y)].add_block(x % Settings.get_chunk_size(), y,
                                                      z % Settings.get_chunk_size(), which_side, block_type)

    def where_add_side(self, x, y, z):
        which_side = ""
        which_side += self.check_side(x, y + 1, z, "t")  # top
        which_side += self.check_side(x, y - 1, z, "d")  # down

        which_side += self.check_side(x, y, z - 1, "b")  # back
        which_side += self.check_side(x, y, z + 1, "f")  # front

        which_side += self.check_side(x + 1, y, z, "r")  # right
        which_side += self.check_side(x - 1, y, z, "l")  # left

        return which_side

    def check_side(self, x, y, z, which_side):
        return which_side if self.return_world(x, y, z) in TRANSPARENT_BLOCKS else ""

    def add_structures_to_chunk(self, x_basic, z_basic):
        how_many = random.randint(0, 7)

        for i in range(how_many):
            x = x_basic * Settings.get_chunk_size() + random.randint(0, 15)
            z = z_basic * Settings.get_chunk_size() + random.randint(0, 15)
            # print(x, z)
            y = self.return_height(x, 140, z)
            if self.return_world(x, y, z) in (1, 2):
                self.add_tree(x, y, z)
            elif self.return_world(x, y, z) == 4:
                self.add_cactus(x, y, z)

    def add_block_before_generating_chunk(self, x, y, z, block_type):
        chunk_x, chunk_y = which_chunk(x, z)
        if not (chunk_x, chunk_y) in self.dic_chunks:
            self.add_new_chunk(chunk_x, chunk_y)
        # print(x, y, z)
        self.dic_chunks[(chunk_x, chunk_y)].world[x % Settings.get_chunk_size(),
                                                  y, z % Settings.get_chunk_size()] = block_type

    def add_tree(self, x, y, z):
        tree_height = random.randint(5, 8)
        for i in range(1, tree_height):
            self.add_block_before_generating_chunk(x, y + i, z, 5)

        for i in (-2, -1, 0, 1, 2):
            for j in (-2, -1, 0, 1, 2):
                self.add_block_depends_on_chunk(x + i, y + tree_height - 1, z + j, 6)
                self.add_block_depends_on_chunk(x + i, y + tree_height, z + j, 6)

    def add_block_depends_on_chunk(self, x, y, z, block_type):
        chunk_x, chunk_y = which_chunk(x, z)
        if self.return_world(x, y, z) == 0:
            if (chunk_x, chunk_y) in self.fully_completed:
                self.add_block(x, y, z, block_type)
            else:
                self.add_block_before_generating_chunk(x, y, z, block_type)

    def add_cactus(self, x, y, z):
        cactus_height = random.randint(2, 5)
        for i in range(1, cactus_height):
            self.add_block_before_generating_chunk(x, y + i, z, 7)
    # -------------------------------------------------------------------------------

    def delete_sides(self, x, y, z, which_side):
        x, y, z = floor_for_coords(x, y, z)
        return self.dic_chunks[which_chunk(x, z)].delete_block_from_batch(x % 16, y, z % 16, which_side)

    def check_and_delete_sides(self, x, y, z, which_side):
        x, y, z = floor_for_coords(x, y, z)
        self.dic_chunks[which_chunk(x, z)].check_and_delete_sides(x % 16, y, z % 16, which_side)

    def return_world(self, x, y, z):
        x, y, z = floor_for_coords(x, y, z)
        return self.dic_chunks[which_chunk(x, z)].\
            return_world(x % Settings.get_chunk_size(),
                         y, z % Settings.get_chunk_size()) if which_chunk(x, z) in self.dic_chunks else 0

    def return_height(self, x, y, z):
        chunk_x, chunk_y = which_chunk(x, z)
        x, y, z = floor_for_coords(x, y, z)
        return self.dic_chunks[(chunk_x, chunk_y)].\
            return_height(x % Settings.get_chunk_size(), y, z % Settings.get_chunk_size()) \
            if (chunk_x, chunk_y) in self.dic_chunks else 50

    def check_and_add_sides(self, x, y, z, which_side):
        x, y, z = floor_for_coords(x, y, z)
        self.dic_chunks[which_chunk(x, z)].\
            check_and_add_sides(x % Settings.get_chunk_size(), y, z % Settings.get_chunk_size(), which_side)

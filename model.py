from pyglet.gl import *
import math

from save import ChunkSave


def which_chunk(x):
    return math.floor(x/16)


def return_angle(x, y):
    if x == 0:
        return 90 if y > 0 else 270
    angle = math.degrees(math.atan(y / x)) if x > 0 else math.degrees(math.atan(y / x)) + 180
    return angle % 360


class Model:
    PLAYER_SIZE = 0.2

    def __init__(self):
        self.dic_chunks = {}
        self.is_there_new = False

    def draw(self, x, y, how_far, angle):
        self.is_there_new = False
        self.draw_old_chunks(x, y)
        ile_zrobionych = 0
        ile_pominietych = 0
        for k in range(1, how_far):
            for i, j in ((x, y) for x in range(-k, k + 1) for y in range(-k, k + 1) if abs(x) + abs(y) == k):
                if self.is_visible(angle, i, j) or k < 3:
                    ile_zrobionych += 1
                    self.draw_old_chunks(x + i, y + j)
                    # if k == 1 :
                    #     self.dic_chunks.get((x + i, y + j)).generate_chunk()
                else:
                    ile_pominietych += 1
                    # print(self.return_angle(i, j), angle)
                # self.draw_old_chunks(x + i, y + j)
        # print(ile_zrobionych, ile_pominietych)

    def draw_old_chunks(self, x, y):
        if self.is_created(x, y):
            self.draw_one(x, y)
        elif not self.is_there_new:
            self.draw_one(x, y)
            self.is_there_new = True

    def is_created(self, x, y):
        return (x, y) in self.dic_chunks

    def draw_one(self, x, y):
        if not self.is_created(x, y):
            self.dic_chunks[(x, y)] = ChunkSave(x, y)
        self.dic_chunks.get((x, y)).draw()

    def return_height(self, x, y, z):
        chunk_x = math.floor(x/16)
        chunk_y = math.floor(z/16)

        return self.dic_chunks.get((chunk_x, chunk_y)).return_height(int(x % 16), int(y), int(z % 16))\
            if (chunk_x, chunk_y) in self.dic_chunks else 50

    def return_max_height(self, x, y, z):
        max_height = 0
        for i in (-self.PLAYER_SIZE, 0, self.PLAYER_SIZE):
            for j in (-self.PLAYER_SIZE, 0, self.PLAYER_SIZE):
                max_height = max(max_height, self.return_height(x + i, y, z + j))

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

    def delete_block(self, x, y, z):
        x = int(x)
        y = int(y)
        z = int(z)
        # print("pozycja: ", x, y, z)
        chunk_x = which_chunk(x)
        chunk_y = which_chunk(z)
        if self.dic_chunks[(chunk_x, chunk_y)].return_world(x % 16, y, z % 16) == 0:
            return False
        where = "bflrdtu"
        # print("klocek usuniety: ", x, y, z, " na chunku ", chunk_x, chunk_y)
        if which_chunk(x + 1) != chunk_x:
            self.dic_chunks[(chunk_x + 1, chunk_y)].check_and_add((x+1) % 16, y, z % 16, "l")
            where = where.replace('l', '')
            # print("1: ", self.dic_chunks[(chunk_x + 1, chunk_y)], self.dic_chunks[(chunk_x, chunk_y)])
        elif which_chunk(x - 1) != chunk_x:
            self.dic_chunks[(chunk_x - 1, chunk_y)].check_and_add((x - 1) % 16, y, z % 16, "r")
            where = where.replace('r', '')
            # print("2: ", where)

        if which_chunk(z + 1) != chunk_y:
            self.dic_chunks[(chunk_x, chunk_y + 1)].check_and_add(x % 16, y, (z + 1) % 16, "b")
            where = where.replace('b', '')
        elif which_chunk(z - 1) != chunk_y:
            self.dic_chunks[(chunk_x, chunk_y - 1)].check_and_add(x % 16, y, (z - 1) % 16, "f")
            where = where.replace('f', '')

        if self.is_created(chunk_x, chunk_y):
            self.dic_chunks[(chunk_x, chunk_y)].delete_from_batch(x % 16, y, z % 16, where)

        return True

    def add_block(self, x, y, z, block_type=1):
        x = int(x)
        y = int(y)
        z = int(z)
        chunk_x = which_chunk(x)
        chunk_y = which_chunk(z)
        if self.dic_chunks[(chunk_x, chunk_y)].return_world(x % 16, y, z % 16) != 0:
            return False
        where = self.dic_chunks[(chunk_x, chunk_y)].where_add_block(x, y, z) + "a"
        # print("klocek usuniety: ", x, y, z, " na chunku ", chunk_x, chunk_y)
        if which_chunk(x + 1) != chunk_x:
            if self.dic_chunks[(chunk_x + 1, chunk_y)].return_world((x+1) % 16, y, z % 16) != 0:
                self.dic_chunks[(chunk_x + 1, chunk_y)].delete_from_batch((x+1) % 16, y, z % 16, "l")
                where = where.replace('r', '')
                print("cos")
            # print("1: ", self.dic_chunks[(chunk_x + 1, chunk_y)], self.dic_chunks[(chunk_x, chunk_y)])
        elif which_chunk(x - 1) != chunk_x:
            if self.dic_chunks[(chunk_x - 1, chunk_y)].return_world((x - 1) % 16, y, z % 16) != 0:
                self.dic_chunks[(chunk_x - 1, chunk_y)].delete_from_batch((x - 1) % 16, y, z % 16, "r")
                where = where.replace('l', '')
            # print("2: ", where)
        #
        # if which_chunk(z + 1) != chunk_y:
        #     self.dic_chunks[(chunk_x, chunk_y + 1)].check_and_add(int(x % 16), int(y), int((z + 1) % 16), "b")
        #     where = where.replace('b', '')
        # elif which_chunk(z - 1) != chunk_y:
        #     self.dic_chunks[(chunk_x, chunk_y - 1)].check_and_add(int(x % 16), int(y), int((z - 1) % 16), "f")
        #     where = where.replace('f', '')
        # if self.is_created(chunk_x, chunk_y):
        self.dic_chunks[(chunk_x, chunk_y)].add_block(x % 16, y, z % 16, where, block_type)
        return True

    def return_world(self, x, y, z):
        x = int(x)
        y = int(y)
        z = int(z)
        return self.dic_chunks[(which_chunk(x), which_chunk(z))].return_world(x % 16, y, z % 16)

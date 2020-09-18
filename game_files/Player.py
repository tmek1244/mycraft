import math

from pyglet.window import key
from pyglet.window import mouse

from game_files.equipment import Equipment


def sign(x):
    return math.copysign(1, x)


class Player:
    PLAYER_HEIGHT = 2.8

    def __init__(self, model, pos=(0, 0, 0), rot=(0, 0)):
        self.pos = list(pos)
        self.rot = list(rot)
        self.time = 0
        self.in_jump = False
        self.model = model
        self.height = 0
        self.eq = Equipment()
        self.item = 0

    def mouse_motion(self, dx, dy):
        dx /= 8
        dy /= 8
        self.rot[0] -= dx
        self.rot[1] += dy
        if self.rot[1] > 90:
            self.rot[1] = 90
        elif self.rot[1] < -90:
            self.rot[1] = -90

    def mouse_press(self, button):
        # print(self.pos)
        if button == mouse.LEFT:
            x, y, z, too_far = self.calculate_coordinates("remove")
            if not too_far:
                self.eq.add_item(self.model.return_deleted_block(x, y, z))
                # print(self.eq.print_content())

        if button == mouse.RIGHT:
            x, y, z, too_far = self.calculate_coordinates("add")
            if not too_far and not self.is_there_player(x, y, z):
                item_to_add = self.eq.take_item(self.item)
                if item_to_add != 0:
                    self.model.add_block(x, y, z, item_to_add)
            # print(self.is_there_player(x, y, z))

    def calculate_coordinates(self, which_block):
        delta = 0.001
        v_x, v_y, v_z = self.calculate_vector()
        x, y, z = self.pos[0], self.pos[1], self.pos[2]
        too_far = False
        while self.model.return_world(x, y, z) == 0 and self.distance(x, y, z) < 5:
            x += delta*v_x
            y += delta*v_y
            z += delta*v_z
            if self.distance(x, y, z) > 5:
                too_far = True

        if which_block == "add":
            return math.floor(x - delta*v_x), int(y - delta*v_y), math.floor(z - delta*v_z), too_far
        else:
            return math.floor(x), int(y), math.floor(z), too_far

    def is_there_player(self, x, y, z):
        player_x = math.floor(self.pos[0])
        player_y = math.floor(self.pos[1])
        player_z = math.floor(self.pos[2])

        x, y, z = int(x), int(y), int(z)
        # print(x, y, z, self.pos)

        if (x, y, z) != (player_x, player_y, player_z) and (x, y, z) != (player_x, player_y - 1, player_z)\
                and (x, y, z) != (player_x, math.floor(self.pos[1] - 1.79), player_z):
            return False
        return True

    def distance(self, x, y, z):
        return math.sqrt((x - self.pos[0])**2 + (y - self.pos[1])**2 + (z - self.pos[2])**2)

    def calculate_vector(self):
        y = math.sin(math.radians(self.rot[1]))
        d = math.cos(math.radians(self.rot[1]))
        z = -math.cos(math.radians(self.rot[0]))*d
        x = -math.sin(math.radians(self.rot[0]))*d

        return x, y, z

    def update(self, dt, keys):
        if dt > 0:
            self.keyboard_manager(dt, keys)
            self.gravity(dt)

    def keyboard_manager(self, dt, keys):
        self.height = self.model.return_height(self.pos[0], self.pos[1], self.pos[2])
        # print(self.height, self.pos[1])

        speed = dt * 5
        if keys[key.LSHIFT]:
            speed *= 2

        rotY = -self.rot[0] / 180 * math.pi
        dx, dz = speed * math.sin(rotY), speed * math.cos(rotY)
        if keys[key.SPACE]:
            self.jump()

        if keys[key.W]:
            self.is_move_possible(dx, -dz)
        if keys[key.S]:
            self.is_move_possible(-dx, +dz)
        if keys[key.A]:
            self.is_move_possible(-dz, -dx)
        if keys[key.D]:
            self.is_move_possible(dz, dx)

        if keys[key.LCTRL]:
            self.pos[1] -= speed

        if keys[key._1]:
            self.item = 0
        if keys[key._2]:
            self.item = 1
        if keys[key._3]:
            self.item = 2
        if keys[key._4]:
            self.item = 3
        if keys[key._5]:
            self.item = 4
        if keys[key._0]:
            self.item = 5
        if keys[key._0]:
            self.item = 6
        if keys[key._0]:
            self.item = 7
        if keys[key._9]:
            self.item = 8
        if keys[key._0]:
            self.item = 9
        # print("Is in air: ", self.is_in_air())

    def is_move_possible(self, dx, dz):
        self.is_move_possible_in_one_axis(dx, 0)
        self.is_move_possible_in_one_axis(dz, 2)

    def is_move_possible_in_one_axis(self, dx, axis):
        if self.model.return_height(self.pos[0] + sign(dx)*(abs(dx)+0.2)*(2 - axis)/2, self.pos[1],
                                    self.pos[2] + sign(dx)*(abs(dx)+0.2)*axis/2) \
                <= self.pos[1] - self.PLAYER_HEIGHT + 0.1:
            self.pos[axis] += dx

    def is_in_air(self):
        height = self.model.return_max_height(self.pos)
        if height + self.PLAYER_HEIGHT >= self.pos[1]:
            return False
        return True

    def jump(self):
        if not self.is_in_air():
            self.in_jump = True
            self.time = 0.3

    def gravity(self, dt):
        if self.in_jump and self.time > 0:
            self.during_uprise(dt)
        else:
            self.during_the_fall(dt)

    def jump_speed(self, dt):
        return 1.5 * dt / 0.3 if self.time > 0 else 8*dt**2 - 15*self.time*dt

    def during_uprise(self, dt):
        self.height = self.model.return_height(self.pos[0], self.pos[1] + self.jump_speed(dt), self.pos[2])
        self.time = max(self.time - dt, 0)
        if self.pos[1] + self.jump_speed(dt) >= self.height + self.PLAYER_HEIGHT:
            self.pos[1] += self.jump_speed(dt)
        else:
            self.in_jump = False

    def during_the_fall(self, dt):
        height_max = self.model.return_max_height(self.pos)
        if self.is_in_air():
            self.time -= dt
            self.pos[1] = max(self.pos[1] - self.jump_speed(dt), height_max + self.PLAYER_HEIGHT)
        else:
            self.time = 0


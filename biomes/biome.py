import noise
import numpy as np


class Biome:
    WIDTH = 16
    LENGTH = 16
    HEIGHT = 150
    OFFSET = 0.02
    HEIGHT_OF_TERRAIN = 40

    @staticmethod
    def add(world, x, z, poz_x, poz_z):
        pass

    @staticmethod
    def return_height(x_off, z_off):
        return int(Biome.HEIGHT_OF_TERRAIN * np.abs(noise.pnoise2(x_off, z_off)) +
                   (Biome.HEIGHT - Biome.HEIGHT_OF_TERRAIN))

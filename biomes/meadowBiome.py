from biomes.biome import Biome


class MeadowBiome(Biome):

    @staticmethod
    def add(world, x, z, poz_x, poz_z):
        x_off = (poz_x + x) * Biome.OFFSET
        z_off = (poz_z + z) * Biome.OFFSET
        height = Biome.return_height(x_off, z_off)
        for y in range(1, height - 2):
            world[x, y, z] = 3
        world[x, height - 2, z] = 2
        world[x, height - 1, z] = 2
        world[x, height, z] = 1

        return height

import os

from ..image import AbstractTiledImage, ImagePyramid


class NaturalEarth2Image(AbstractTiledImage):
    NUM_LEVEL_0_TILES = 2, 1
    TILE_SIZE = 256

    @staticmethod
    def get_pyramid():
        """
        Return an instance of a 'Natural Earth v2' image pyramid:
        * global coverage
        * JPEG RGB format
        * 3 levels of detail: 0 to 2
        * tile size: 256 pixels
        * 2 x 1 tiles on level zero
        """

        dir_path = os.path.join(os.path.dirname(__file__), 'NaturalEarth2')
        return ImagePyramid(NaturalEarth2Image.NUM_LEVEL_0_TILES,
                            (NaturalEarth2Image.TILE_SIZE, NaturalEarth2Image.TILE_SIZE),
                            [NaturalEarth2Image(dir_path, level) for level in (0, 1, 2)])

    def __init__(self, dir_path, z_index):
        factor = 1 << z_index
        num_tiles_x = factor * NaturalEarth2Image.NUM_LEVEL_0_TILES[0]
        num_tiles_y = factor * NaturalEarth2Image.NUM_LEVEL_0_TILES[1]
        tile_size = NaturalEarth2Image.TILE_SIZE
        self._z_index = z_index
        self._base_path = '%s/%d' % (dir_path, z_index)
        super().__init__((num_tiles_x * tile_size, num_tiles_y * tile_size),
                         tile_size=(tile_size, tile_size),
                         num_tiles=(num_tiles_x, num_tiles_y), format='JPEG', mode='RGB')

    def get_tile(self, tile_x, tile_y):
        num_tiles_y = self.num_tiles[1]
        path = '%s/%d/%d.jpg' % (self._base_path, tile_x, num_tiles_y - 1 - tile_y)
        with open(path, 'rb') as fp:
            return fp.read()


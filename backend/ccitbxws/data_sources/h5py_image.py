import numpy as np
from ..image import OpImage, ImagePyramid, create_ndarray_downsampling_image
from ..utils import compute_tile_size


class H5PyDatasetImage(OpImage):
    def __init__(self, h5_dataset, tile_size=None):
        self._h5_dataset = h5_dataset
        width, height = h5_dataset.shape[-1], h5_dataset.shape[-2]
        if tile_size is None:
            if h5_dataset.chunks:
                chunk_width, chunk_height = h5_dataset.chunks[-1], h5_dataset.chunks[-2]
            else:
                chunk_width, chunk_height = None, None
            tile_size = (compute_tile_size(width, chunk_size=chunk_width),
                         compute_tile_size(height, chunk_size=chunk_height))
        mode = str(h5_dataset.dtype)
        super().__init__((width, height), tile_size=tile_size, format='ndarray', mode=mode)

    @property
    def h5_dataset(self):
        return self._h5_dataset

    def compute_tile(self, tile_x, tile_y, rectangle):
        x, y, w, h = rectangle
        tile = self._h5_dataset[:, y:y + h, x:x + w]
        _, dh, dw = tile.shape
        fill_value = self._h5_dataset.fillvalue

        if dh < h or dw < w:
            # if original size is less than tile size, force tile size and fill with suitable background value
            if fill_value is not None:
                background_value = fill_value
            else:
                if np.issubdtype(tile.dtype, float) or np.issubdtype(tile.dtype, complex):
                    background_value = np.nan
                else:
                    background_value = 0
            new_data = np.full((1, h, w), background_value, dtype=tile.dtype)
            new_data[:, 0:dh, 0:dw] = tile
            tile = new_data

        if not np.ma.is_masked(tile):
            # if tile is not masked
            if fill_value is not None:
                # and we have a fill value, return a masked tile
                tile = np.ma.masked_equal(tile, fill_value)
            elif np.issubdtype(tile.dtype, float) or np.issubdtype(tile.dtype, complex):
                # and it is of float type, return a masked tile with a mask from invalids, i.e. NaN, -Inf, +Inf
                tile = np.ma.masked_invalid(tile)

        return tile

    def create_pyramid(self, **kwargs):
        return ImagePyramid.create_from_image(self, create_ndarray_downsampling_image, **kwargs)



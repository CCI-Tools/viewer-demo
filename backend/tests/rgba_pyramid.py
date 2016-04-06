import os
import time

import h5py

import ccitbxws.data_sources as ds
import ccitbxws.main as main
from ccitbxws.image import ColorMappedRgbaImage

data_root = main.CONFIG.get('DATA_ROOT', '.')
file_path = os.path.join(data_root, 'ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201301-fv2.0.nc')
file = h5py.File(file_path, 'r')
dataset = file['chlor_a']


image = ColorMappedRgbaImage(ds.H5PyDatasetImage(dataset, tile_size=(270, 270)),
                             value_range=(0.0, 2.0))
num_tiles_x, num_tiles_y = image.num_tiles
dirname = 'chlor_a'
if not os.path.exists(dir):
    os.mkdir(dirname)

t1 = time.clock()
for tile_y in range(num_tiles_y):
    for tile_x in range(num_tiles_x):
        tile = image.get_tile(tile_x, tile_y)
        tile.save(dirname + '/%d_%d.png' % (tile_y, tile_x), format='PNG')
t2 = time.clock()

print("saving RGBA tiles took: ", t2 - t1)

file.close()

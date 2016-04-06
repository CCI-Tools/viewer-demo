# See https://pillow.readthedocs.org/en/3.1.x/index.html
# See http://fadeit.dk/blog/post/python3-flask-pil-in-memory-image

import numpy as np
from PIL import Image
import io

# Construct silly image

array = 255. * np.random.rand(512, 1024)
array[128:128+256,256:256+512] = np.full((256, 512), 255.)
im = Image.fromarray(array)
im = im.convert('RGBA')
im.show('Raw Image')

# Save image in png_bytes (which may go into a cache dict)

ostream = io.BytesIO()
im.save(ostream, format='PNG')
png_bytes = ostream.getvalue()
ostream.close()

# Open image from png_bytes (which may come from the cache dict)

istream = io.BytesIO(png_bytes)
im = Image.open(istream)
im.load()
istream.close()
im.show('PNG Image')

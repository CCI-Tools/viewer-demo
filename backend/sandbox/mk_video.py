# from https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python/34555939#34555939

import sys

sys.path.append('C:\\Users\\Norman\\.snap\\snap-python')

import cv2
import io
import matplotlib.cm as cm
import numpy as np
import math
from PIL import Image

import snappy
from snappy import ProductIO

jpy = snappy.jpy

# More Java type definitions required for image generation
Color = jpy.get_type('java.awt.Color')
ColorPoint = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef$Point')
ColorPaletteDef = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef')
ImageInfo = jpy.get_type('org.esa.snap.core.datamodel.ImageInfo')
ImageManager = jpy.get_type('org.esa.snap.core.image.ImageManager')
JAI = jpy.get_type('javax.media.jai.JAI')


def write_image(band, points, filename, format):
    print("writing " + filename)
    cpd = ColorPaletteDef(points)
    ii = ImageInfo(cpd)
    band.setImageInfo(ii)
    im = ImageManager.getInstance().createColoredBandImage([band], band.getImageInfo(), 0)
    JAI.create("filestore", im, filename, format)


def write_images(file):
    # Disable JAI native MediaLib extensions
    System = jpy.get_type('java.lang.System')
    System.setProperty('com.sun.media.jai.disableMediaLib', 'true')

    NUM_BANDS = 15

    product = ProductIO.readProduct(file)
    band_arrays = []
    w = product.getSceneRasterWidth()
    h = product.getSceneRasterHeight()
    for i in range(0, NUM_BANDS):
        band = product.getBand("radiance_%d" % (i + 1))
        band_data = np.zeros(w * h, dtype=np.float32)
        band.readPixels(0, 0, w, h, band_data)
        band_arrays.append(band_data)

    result = []
    value_min = -1
    value_max = 1
    for i in range(0, NUM_BANDS):
        for j in range(i + 1, NUM_BANDS):
            a1 = band_arrays[i]
            a2 = band_arrays[j]
            array = (a1 - a2) / (a1 + a2)

            array = np.ma.masked_invalid(array)
            array = array.clip(value_min, value_max)
            array -= value_min
            array *= 1.0 / (value_max - value_min)
            array.shape = (h, w)
            array = cm.jet(array, bytes=True)

            image = Image.fromarray(array, 'RGBA')
            name = 'radiance_%d_to_%d.png' % (i + 1, j + 1)
            with io.FileIO(name, 'w') as fp:
                print('Writing ' + name)
                image.save(fp, format='PNG')
                result.append(name)

    return result


def write_video(frame_names):
    vvw = cv2.VideoWriter('radiance.avi', cv2.VideoWriter_fourcc('F', 'M', 'P', '4'), 10, (1121, 1025))
    for i in range(len(frame_names)):
        print('Adding ' + frame_names[i])
        frame = cv2.imread(frame_names[i])
        vvw.write(frame)
    for j in range(1, len(frame_names) - 1):
        i = len(frame_names) - 1 - j
        print('Adding ' + frame_names[i])
        frame = cv2.imread(frame_names[i])
        vvw.write(frame)


frame_names = write_images("D:\\EOData\\MERIS\\L1\\MER_RR__1PNBCG20050709_101121_000001802038_00466_17554_0001.N1")
write_video(frame_names)

import io
import time
from threading import RLock

from PIL import Image


def _compute_image_size(im):
    mode = im.mode
    pixel_size = 1
    if mode == '1':  # (1-bit pixels, black and white, stored with one pixel per byte)
        pixel_size = 1.0 / 8.0
    if mode == 'L':  # (8-bit pixels, black and white)
        pixel_size = 1
    if mode == 'P':  # (8-bit pixels, mapped to any other mode using a color palette)
        pixel_size = 1
    if mode == 'RGB':  # (3x8-bit pixels, true color)
        pixel_size = 3
    if mode == 'RGBA':  # (4x8-bit pixels, true color with transparency mask)
        pixel_size = 4
    if mode == 'CMYK':  # (4x8-bit pixels, color separation)
        pixel_size = 4
    if mode == 'YCbCr':  # (3x8-bit pixels, color video format)
        pixel_size = 3
    if mode == 'LAB':  # (3x8-bit pixels, the L*a*b color space)
        pixel_size = 3
    if mode == 'HSV':  # (3x8-bit pixels, Hue, Saturation, Value color space)
        pixel_size = 3
    if mode == 'I':  # (32-bit signed integer pixels)
        pixel_size = 4
    if mode == 'F':  # (32-bit floating point pixels)
        pixel_size = 4
    return im.width * im.height * pixel_size


def _get_format_from_mode(mode):
    if mode == '1':  # (1-bit pixels, black and white, stored with one pixel per byte)
        return 'RAW'
    if mode == 'I':  # (32-bit signed integer pixels)
        return 'RAW'
    if mode == 'F':  # (32-bit floating point pixels)
        return 'RAW'
    return 'PNG'


# Getting Started

Create file `./ccitbxws-config.py` and adjust content like so:

    # DATA_ROOT is used to resolve relative file paths passed to the web service
    DATA_ROOT = 'C:\\Users\\Norman\\EOData\\occci-v2.0\\geographic\\netcdf\\monthly\\chlor_a\\2013'

Then type to build the web service stand-alone tool `ccitbxws`:

    $ python3 setup.py develop

and start Python web service

    $ ccitbxws

In a browser, type some REST URL like so:

    http://127.0.0.1:8080/ccitbx/ne2/0/0/0.jpg


# Libraries worth considering

* https://github.com/Itseez/opencv - OpenCV (Open Source Computer Vision Library: http://opencv.org) is an open-source
  BSD-licensed library that includes several hundreds of computer vision algorithms.
* https://github.com/mapbox/rasterio - Rasterio is designed to make working with geospatial raster data more
  productive and more fun.

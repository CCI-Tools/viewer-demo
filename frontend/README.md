# Getting started

0. Install [Node.js](https://nodejs.org/en/download/) to get the JavaScript package manager `npm`
1. cd `../frontend` and run `npm install .`
2. Download and unpack [Cesium](https://cesiumjs.org/). You should now have:
    * `prototype2/`
      * `backend/`
      * `frontend/`
        * `Cesium-1.17/`
          * `Source/`
          * `Build/`
          * ...
        * `node_modules/`
          * `electron-prebuild/`
          * `jquery/`
          * `jquery-ui/`
3. `cd ../backend` and start Python web service. See `../backend/README.md`.
4. `cd ../frontend` and type `electron .`

For easier testing you can also create a file `ccitbxui.cmd` or `ccitbxui.sh` and start the frontend with
NetCDF file arguments. E.g. in `ccitbxui.cmd` put:

    electron . D:\EOData\CCI-TBX\occci-v2.0\geographic\netcdf\monthly\chlor_a\2013\ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201302-fv2.0.nc


# Next Steps

## Performance Evaluation TODOs

- Implement client side rendering of images
- Read Glaciers shapefiles (via Cesium CZML)
- Extract time series at given lat/lon position, add time-series plot
- Implement movie from e.g. OC/SST time series
- Rectangle/Polygon tool, create ROI, extract data from ROI
- Open multiple files, add open file window
- Add layers from multiple files to layers window
- Add multiple Cesium viewers
- Add fast offline base layer, so that we avoid extra load caused by remote tiles
- Move layers up and down

## Nice to have TODOs

- Set initial positions of windows
- Store/restore positions of windows in/from preferences
- Start webservice from main.js (for how to, see DeDop sandbox)
- Combine file + variable window, use jquery-ui accordion
- Add tooltip texts to color map categories
- Improve software design
  * Modularise code in index.html, use requirejs
  * Extract abstract tool window class: Show action, HTML, ViewModel
  * Add tool window manager to app instance
  * Separate imagery layer from variable. Layers list shall be for single Cesium instance only.
    Variable lists must be independent of Cesium viewer.

# More Ideas

- Integrate a second, SNAP WS (see [prototype1](../prototype1), so that we can also ingest Sentinel data!
- Using an off-line base layer, e.g. [Narural Earth II](http://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/), will improve performance and ensure
  working off line
- Add ECV overview window showing coloured ECV bars: vert. axis : ECV, hor. axis: time (years), see Ed's LivingPlanet notes.
  Also, from SoW: _The GUI tool shall include the following parts:_
  * display of all ECVs with capability to filter
  * geospatial (3D globe and 2D map) display of output with capability to portray vertical profile datasets and select map projection.
  * Temporal filter
  * Processor selection The user shall be able to click and drill down on a processor to define it and view configuration etc.
  * Output format selection
- Integrate Jupyter notebook, run with CCITBXWS or connect to existing CCITBXWS. Simple use case:

```bash
    $ sst1 = ccitb.get_ecv('SST', year=2015)
    $ sst2 = ccitb.get_ecv('SST', year=2016)
    $ sst_dev = numpy.sqrt(sst2 - sst1)
    $ ccitb.open_in_ui(sst_dev)
```

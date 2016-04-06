import base64
import json
import os
import pprint
import sys
import time
from datetime import datetime
from threading import current_thread, Lock

import cherrypy
import falcon
import h5py
import numpy

from ccitbxws.cmaps import get_cmaps
from ccitbxws.image import ColorMappedRgbaImage, ImagePyramid, TransformArrayImage

__version__ = '0.0.1'

CONFIG = {}
_CONFIG_FILE = './ccitbxws-conf.py'
_JOBS = {}
_DATASETS = {}
PYRAMIDS = dict()
GLOBAL_LOCK = Lock()


# see http://stackoverflow.com/questions/3488934/simplejson-and-numpy-array/
class Base64NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        If input object is an ndarray it will be converted into a dict
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, numpy.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = numpy.ascontiguousarray(obj)
                assert (cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(data=data_b64.decode('unicode_escape'),
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class SimpleNumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            if obj.ndim == 1:
                return obj.tolist()
            else:
                return [self.default(obj[i]) for i in range(obj.shape[0])]
        return json.JSONEncoder.default(self, obj)


def json_numpy_object_hook(dct):
    """
    Decodes a previously encoded numpy ndarray with proper shape and dtype.
    :param dct: (dict) JSON-encoded ndarray
    :return: (ndarray) if input was an encoded ndarray, else the unchanged dct
    """
    if isinstance(dct, dict) and 'data' in dct and 'dtype' in dct and 'shape' in dct:
        data = base64.b64decode(dct['data'])
        return numpy.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct


def _get_file_from_req(req, required=True):
    file = req.get_param('file', required=required)
    if file:
        return _get_norm_path(file)
    return None


def _get_param_as_float(req, name, default=None):
    str_value = req.get_param(name, required=default is None)
    if str_value is not None:
        try:
            return float(str_value)
        except ValueError:
            raise falcon.HTTPBadRequest('Illegal query parameter', 'parameter \'%s\' must be a float')
    return default


def _get_norm_path(file_name):
    if os.path.isabs(file_name):
        file_path = file_name
    else:
        data_root = CONFIG.get('DATA_ROOT', '.')
        file_path = os.path.join(data_root, file_name)
    file_path = os.path.normpath(file_path)
    return file_path


def _open_dataset_from_req(req):
    return _open_dataset(_get_file_from_req(req))


def _open_dataset(file_path):
    if file_path in _DATASETS:
        dataset = _DATASETS[file_path]
    else:
        dataset = h5py.File(file_path, 'r')
        _DATASETS[file_path] = dataset
    return dataset


def _close_dataset(file_path):
    if file_path in _DATASETS:
        dataset = _DATASETS[file_path]
        del _DATASETS[file_path]
        dataset.close()
        return True
    return False


def _get_unicode_attr(attr, key, default_value=''):
    if key in attr:
        value = attr.get(key)
        #print(key, ' type:', str(type(value)), ' value:', str(value))
        if type(value) == bytes or type(value) == numpy.bytes_:
            return value.decode('unicode_escape')
        elif type(value) != str:
            return str(value)
        else:
            return value
    return default_value


def _get_float_attr(attr, key, default_value=None):
    if key in attr:
        try:
            return float(attr.get(key))
        except:
            pass
    return default_value


def _read_python_config_file(file):
    config = {}
    with open(file, 'r') as fp:
        code = fp.read()
        exec(code, None, config)
    return config


if os.path.exists(_CONFIG_FILE):
    CONFIG = _read_python_config_file(_CONFIG_FILE)
else:
    print('WARNING: missing file %s, please refer to README.md' % _CONFIG_FILE)

print('CONFIG = ')
pprint.pprint(CONFIG)


def _get_variable_info(variable):
    # See http://docs.h5py.org/en/latest/
    # print(list(variable.attrs.keys()))
    for dim in variable.dims:
        print(variable.name, '.dim:', dim)
        for key in dim.keys():
            value = dim[key]
            print(variable.name, '.dim.', key, '=', value)

    attrs = variable.attrs
    variable_info = {
        'name': variable.name,
        'dtype': str(variable.dtype),
        'ndim': len(variable.dims),
        'shape': variable.shape,
        'chunks': variable.chunks,
        # 'dimensions': variable.dimensions,
        'fill_value': _get_float_attr(attrs, '_FillValue',
                                      default_value=float(variable.fillvalue) if variable.fillvalue else None),
        'valid_min': _get_float_attr(attrs, 'valid_min'),
        'valid_max': _get_float_attr(attrs, 'valid_max'),
        'add_offset': _get_float_attr(attrs, 'add_offset'),
        'scale_factor': _get_float_attr(attrs, 'scale_factor'),
        'standard_name': _get_unicode_attr(attrs, 'standard_name'),
        'long_name': _get_unicode_attr(attrs, 'long_name'),
        'units': _get_unicode_attr(attrs, 'units', default_value='-'),
        # todo - fix code below, it seems to originate from an h5py internal bug
        #  File "C:\Python34-amd64\lib\site-packages\h5py\_hl\attrs.py", line 55, in __getitem__
        #     raise IOError("Empty attributes cannot be read")
        # 'comment': _get_unicode_attr(attrs, 'comment'),
    }
    if is_lat_lon_image_variable(variable):
        variable_info['imageConfig'] = _get_variable_image_config(variable)
    return variable_info


def _get_variable_image_config(variable):
    t1 = time.clock()
    max_size, tile_size, num_level_zero_tiles, num_levels = ImagePyramid.compute_layout(array=variable)
    t2 = time.clock()
    print("PERF: ImagePyramid.compute_layout took %f seconds" % (t2 - t1))
    return {
        # todo - compute imageConfig.sector from variable attributes. See frontend todo.
        'sector': {
            'minLongitude': -180.0,
            'minLatitude': -90.0,
            'maxLongitude': 180.0,
            'maxLatitude': 90.0
        },
        'numLevels': num_levels,
        'numLevelZeroTilesX': num_level_zero_tiles[0],
        'numLevelZeroTilesY': num_level_zero_tiles[1],
        'tileWidth': tile_size[0],
        'tileHeight': tile_size[1]
    }


def is_y_flipped(variable):
    lat_var = get_lat_var(variable)
    if lat_var is not None:
        return lat_var[0] < lat_var[1]
    return False


def is_lat_lon_image_variable(variable):
    lon_var = get_lon_var(variable)
    if lon_var is not None and lon_var.shape[0] >= 2:
        lat_var = get_lat_var(variable)
        return lat_var is not None and lat_var.shape[0] >= 2
    return False


def get_lon_var(variable):
    return get_dim_var(variable, ['lon', 'longitude', 'long'], -1)


def get_lat_var(variable):
    return get_dim_var(variable, ['lat', 'latitude'], -2)


def get_dim_var(variable, names, pos):
    if len(variable.dims) >= -pos:
        dim = variable.dims[len(variable.dims) + pos]
        for name in names:
            if name in dim:
                dim_var = dim[name]
                if dim_var is not None and len(dim_var.shape) == 1 and dim_var.shape[0] >= 1:
                    return dim_var
    return None


def _get_time_string_from_file_name(file_name):
    base_name, ext = os.path.splitext(file_name)
    if ext != '.nc':
        return None
    name_parts = base_name.split('-')
    # ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201312-fv2.0
    # ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-20110401-fv0100
    # 20120101120000-ESACCI-L4_GHRSST-SSTfnd-OSTIA-GLOB_DM-v02.0-fv01.0
    time_part = None
    if len(name_parts) == 8 and name_parts[0] == 'ESACCI' and name_parts[1] == 'OC':
        time_part = name_parts[6]
    elif len(name_parts) == 8 and name_parts[0] == 'ESACCI' and name_parts[1] == 'OZONE':
        time_part = name_parts[6]
    elif len(name_parts) == 8 and name_parts[1] == 'ESACCI' and \
            (name_parts[3] == 'SSTfnd' or name_parts[3] == 'SSTdepth'):
        time_part = name_parts[0]
    # print('time_part =', time_part)
    if time_part:
        time_value = None
        if len(time_part) == 6:
            time_value = datetime.strptime(time_part, '%Y%m')
        elif len(time_part) == 8:
            time_value = datetime.strptime(time_part, '%Y%m%d')
        elif len(time_part) == 14:
            time_value = datetime.strptime(time_part, '%Y%m%d%H%M%S')
        if time_value:
            return datetime.strftime(time_value, '%Y-%m-%d %H:%M:%S')
    return None


def crossdomain(req, resp):
    resp.set_header('Access-Control-Allow-Origin', '*')


class FileVarTile:
    def on_get(self, req, resp, z, y, x):
        # GLOBAL_LOCK.acquire()

        file_path = _get_file_from_req(req)
        dataset = _open_dataset(file_path)

        var_name = req.get_param('var', required=True)
        cmap_name = req.get_param('cmap', default='jet')
        cmap_min = _get_param_as_float(req, 'min', default=0.0)
        cmap_max = _get_param_as_float(req, 'max', default=1.0)

        image_id = '%s|%s|%s|%s|%s' % (file_path, var_name, cmap_name, cmap_min, cmap_max)

        global PYRAMIDS
        if image_id in PYRAMIDS:
            pyramid = PYRAMIDS[image_id]
        else:
            variable = dataset[var_name]

            pyramid = ImagePyramid.create_from_array(variable)
            pyramid = pyramid.apply(lambda image: TransformArrayImage(image,
                                                                      no_data_value=variable.fillvalue,
                                                                      force_masked=True,
                                                                      flip_y=is_y_flipped(variable)))
            pyramid = pyramid.apply(lambda image: ColorMappedRgbaImage(image,
                                                                       value_range=(cmap_min, cmap_max),
                                                                       cmap_name=cmap_name,
                                                                       encode=True, format='PNG'))
            PYRAMIDS[image_id] = pyramid
            print('num_level_zero_tiles:', pyramid.num_level_zero_tiles)
            print('num_levels:', pyramid.num_levels)

        print('PERF: >>> Tile:', current_thread(), file_path, var_name, cmap_name, z, y, x)

        t1 = time.clock()
        tile = pyramid.get_tile(int(x), int(y), int(z))
        t2 = time.clock()

        resp.data = tile
        resp.content_type = 'image/png'
        resp.status = falcon.HTTP_OK

        print('PERF: <<< Tile:', current_thread(), file_path, var_name, cmap_name, z, y, x, 'took', t2 - t1, 'seconds')
        # GLOBAL_LOCK.release()


class FileOpen:
    def on_get(self, req, resp):
        file_path = _get_file_from_req(req)
        dataset = _open_dataset(file_path)
        file_attributes = {}
        for attr_name in dataset.attrs:
            file_attributes[attr_name] = _get_unicode_attr(dataset.attrs, attr_name)
        variable_infos = []
        for var_name in dataset.keys():
            variable = dataset[var_name]
            variable_infos.append(_get_variable_info(variable))
        resp.body = json.dumps({
            "filePath": file_path,
            "fileName": os.path.basename(file_path),
            "fileAttributes": file_attributes,
            "variableInfos": variable_infos
        })
        print('resp.body =', resp.body)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class FileClose:
    def on_get(self, req, resp):
        file_path = _get_file_from_req(req)
        _close_dataset(file_path)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class FileVariable:
    def on_get(self, req, resp):
        file_path = _get_file_from_req(req)
        dataset = _open_dataset(file_path)
        var_names = req.get_param_as_list('var')
        resp_data = {}
        if var_names:
            for var_name in var_names:
                if var_name in dataset:
                    variable = dataset[var_name]
                    resp_data[var_name] = _get_variable_info(variable)
        else:
            for var_name in dataset.keys():
                variable = dataset[var_name]
                resp_data[var_name] = _get_variable_info(variable)
        resp.body = json.dumps(resp_data)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class FileTimeSeries:
    def on_get(self, req, resp):
        file_path = _get_file_from_req(req)
        var_name = req.get_param('var', required=True)
        latitude = _get_param_as_float(req, 'lat')
        longitude = _get_param_as_float(req, 'lon')
        print('_______________________ FileTimeSeries:', file_path, var_name, latitude, longitude)
        dir_name = os.path.dirname(file_path)
        file_paths = os.listdir(os.path.dirname(file_path))
        time_series = []
        for file_name in file_paths:
            var_time = _get_time_string_from_file_name(file_name)
            if not var_time:
                continue
            try:
                file_path = os.path.join(dir_name, file_name)
                print('Opening ', file_path)
                if file_path in _DATASETS:
                    dataset = _DATASETS[file_path]
                    must_close = False
                else:
                    dataset = h5py.File(file_path, 'r')
                    must_close = True
                variable = dataset[var_name]
                w = variable.shape[-1]
                h = variable.shape[-2]
                x = int(w * (longitude + 180.) / 360. + 0.5)
                if is_y_flipped(variable):
                    y = int(h * (latitude + 90.) / 180. + 0.5)
                else:
                    y = int(h * (90. - latitude) / 180. + 0.5)
                if x < 0: x = 0
                if y < 0: y = 0
                if x >= w: y = w - 1
                if y >= h: y = h - 1
                print('FileTimeSeries:', x, y, w, h, variable.shape)
                # todo read multiple time values
                if len(variable.shape) == 3:
                    var_value = float(variable[0, y, x])
                elif len(variable.shape) == 2:
                    var_value = float(variable[y, x])
                elif len(variable.shape) == 4:
                    var_value = float(variable[0, 0, y, x])
                else:
                    var_value = None
                if var_value and (numpy.isnan(var_value) or var_value == float(variable.fillvalue)):
                    var_value = None
                if must_close:
                    dataset.close()
            except Exception as e:
                print('FileTimeSeries: Error: ' + str(e))
                var_value = None
            time_series.append([var_time, var_value])

        sorted(time_series, key=lambda item: item[0])
        time_series = list(zip(*time_series))

        print('time_series = ' + str(time_series))

        #resp.body = json.dumps(time_series, cls=SimpleNumpyAwareJSONEncoder)
        resp.body = json.dumps(time_series)
        print('resp.body = ' + resp.body)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class FileMetadata:
    def on_get(self, req, resp):
        file_path = _get_file_from_req(req)
        dataset = _open_dataset(file_path)
        resp.body = json.dumps({'varNames': [var_name for var_name in dataset.keys()]})
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class Test:
    def on_get(self, req, resp):
        resp.body = json.dumps({
            'headers': req.headers,
            'params': req.params
        })
        print('headers:', req.headers)
        print('params:', req.params)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class Exit:
    def on_get(self, req, resp, exit_code=0):
        resp.body = json.dumps(True)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK
        # cherrypy.engine.exit()
        sys.exit(int(exit_code))


class ColorMaps:
    def on_get(self, req, resp):
        resp.body = json.dumps(get_cmaps())
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class About:
    def on_get(self, req, resp):
        resp.body = json.dumps({
            'name': 'ccitbxws',
            'productName': 'CCI Toolbox RESTful WebService',
            'version': __version__,
            'file': __file__,
        })
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_OK


class NE2:
    import ccitbxws.data_sources as ds

    PYRAMID = ds.NaturalEarth2Image.get_pyramid()

    def on_get(self, req, resp, z, y, x):
        # print('NE2.one_get(%s, %s, %s)' % (z, y, x))
        resp.data = NE2.PYRAMID.get_tile(int(x), int(y), int(z))
        resp.content_type = 'image/jpg'
        resp.status = falcon.HTTP_OK


def main(args=sys.argv):
    # Create instance of our CCI Toolbox' RESTful API, which is a WSGI application instance.
    api = falcon.API(after=[crossdomain])
    api.add_route('/ccitbx', About())
    api.add_route('/ccitbx/FileOpen', FileOpen())
    api.add_route('/ccitbx/FileClose', FileClose())
    api.add_route('/ccitbx/FileMetadata', FileMetadata())
    api.add_route('/ccitbx/FileVariable', FileVariable())
    api.add_route('/ccitbx/FileTimeSeries', FileTimeSeries())
    api.add_route('/ccitbx/FileVarTile/{z}/{y}/{x}.png', FileVarTile())
    api.add_route('/ccitbx/ColorMaps', ColorMaps())
    api.add_route('/ccitbx/Test', Test())
    api.add_route('/ccitbx/Exit', Exit())
    api.add_route('/ccitbx/Exit/{exit_code}', Exit())

    # Natural Earth v2 imagery provider for testing, see NaturalEarth2Image class
    api.add_route('/ccitbx/ne2/{z}/{y}/{x}.jpg', NE2())

    # Start a web server with our WSGI application. We use CherryPy here.
    # See docs.cherrypy.org/en/latest/advanced.html?host-a-foreign-wsgi-application-in-cherrypy#host-a-foreign-wsgi-application-in-cherrypy
    cherrypy.tree.graft(api, '/')
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()

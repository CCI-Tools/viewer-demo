from unittest import TestCase

from ccitbxws.main import _get_time_string_from_file_name


class MainTest(TestCase):
    def test_default(self):
        self.assertEqual(
                '2013-12-01 00:00:00',
                _get_time_string_from_file_name(
                        'ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201312-fv2.0.nc'))
        self.assertEqual(
                '2011-04-01 00:00:00',
                _get_time_string_from_file_name(
                        'ESACCI-OZONE-L3S-TC-MERGED-DLR_1M-20110401-fv0100.nc'))
        self.assertEqual(
                '2010-05-01 12:00:00',
                _get_time_string_from_file_name(
                        '20100501120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_LT-v02.0-fv01.1.nc'))
        self.assertEqual(
                '2012-01-01 12:00:00',
                _get_time_string_from_file_name(
                        '20120101120000-ESACCI-L4_GHRSST-SSTfnd-OSTIA-GLOB_DM-v02.0-fv01.0.nc'))
        self.assertEqual(
                None,
                _get_time_string_from_file_name(
                        '20120101120000-ESUPPI-L4_GHRSST-SSTfnd-OSTIA-GLOB_DM-v02.0-fv01.0.nc'))

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc
from scipp.testing import assert_allclose, assert_identical

from plopp import Node
from plopp.data.testing import data_array, dataset
from plopp.plotting.slicer import Slicer


@pytest.mark.usefixtures("_parametrize_interactive_1d_backends")
class TestSlicer1d:
    def test_creation_keep_one_dim_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='single')
        assert sl.slider.value == {'zz': 14, 'yy': 19}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 19]['zz', 14])

    def test_update_keep_one_dim_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='single')
        assert sl.slider.value == {'zz': 14, 'yy': 19}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 19]['zz', 14])
        sl.slider.controls['yy'].value = 5
        assert sl.slider.value == {'zz': 14, 'yy': 5}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 5]['zz', 14])
        sl.slider.controls['zz'].value = 8
        assert sl.slider.value == {'zz': 8, 'yy': 5}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 5]['zz', 8])

    def test_creation_keep_one_dim_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='range')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 0:40]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['yy', 0:40]['zz', 0:30].sum(['yy', 'zz']),
        )

    def test_update_keep_one_dim_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='range')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 0:40]['zz', 0:30])
        sl.slider.controls['yy'].value = (5, 15)
        assert sl.slider.value == {'zz': (0, 29), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 5:16]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['yy', 5:16]['zz', 0:30].sum(['yy', 'zz']),
        )
        sl.slider.controls['zz'].value = (10, 20)
        assert sl.slider.value == {'zz': (10, 20), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 5:16]['zz', 10:21])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['yy', 5:16]['zz', 10:21].sum(['yy', 'zz']),
        )

    def test_creation_keep_one_dim_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 0:40]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['yy', 0:40]['zz', 0:30].sum(['yy', 'zz']),
        )
        # now switch to single mode
        sl.slider.controls['yy'].slider_toggler.value = "-o-"
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (14, 14), 'yy': (19, 19)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 19:20]['zz', 14:15])

    def test_update_keep_one_dim_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 0:40]['zz', 0:30])
        sl.slider.controls['yy'].value = (5, 15)
        sl.slider.controls['zz'].value = (10, 20)
        assert sl.slider.value == {'zz': (10, 20), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 5:16]['zz', 10:21])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['yy', 5:16]['zz', 10:21].sum(['yy', 'zz']),
        )
        # now switch to single mode
        sl.slider.controls['yy'].slider_toggler.value = "-o-"
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        sl.slider.controls['yy'].value = (4, 4)
        sl.slider.controls['zz'].value = (11, 11)
        assert sl.slider.value == {'zz': (11, 11), 'yy': (4, 4)}
        assert_identical(sl.slice_nodes[0].request_data(), da['yy', 4:5]['zz', 11:12])

    def test_with_dataset(self):
        ds = dataset(ndim=2)
        sl = Slicer(ds, keep=['xx'], mode='single')
        nodes = list(sl.figure.graph_nodes.values())
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0].request_data(), ds['a']['yy', 5])
        assert_identical(nodes[1].request_data(), ds['b']['yy', 5])

    def test_with_data_group(self):
        da = data_array(ndim=2)
        dg = sc.DataGroup(a=da, b=da * 2.5)
        sl = Slicer(dg, keep=['xx'], mode='single')
        nodes = list(sl.figure.graph_nodes.values())
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0].request_data(), dg['a']['yy', 5])
        assert_identical(nodes[1].request_data(), dg['b']['yy', 5])

    def test_with_dict_of_data_arrays(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        sl = Slicer({'a': a, 'b': b}, keep=['xx'], mode='single')
        nodes = list(sl.figure.graph_nodes.values())
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0].request_data(), a['yy', 5])
        assert_identical(nodes[1].request_data(), b['yy', 5])

    def test_with_data_arrays_same_shape_different_coord(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        b.coords['xx'] *= 1.5
        Slicer({'a': a, 'b': b}, keep=['xx'], mode='single')

    def test_with_data_arrays_different_shape_along_keep_dim(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        Slicer({'a': a, 'b': b['xx', :10]}, keep=['xx'], mode='single')

    def test_with_data_arrays_different_shape_along_non_keep_dim_raises(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        with pytest.raises(
            ValueError, match='Slicer plot: all inputs must have the same sizes'
        ):
            Slicer({'a': a, 'b': b['yy', :10]}, keep=['xx'], mode='single')

    def test_raises_ValueError_when_given_binned_data(self):
        da = sc.data.table_xyz(100).bin(x=10, y=20)
        with pytest.raises(ValueError, match='Cannot plot binned data'):
            Slicer(da, keep=['xx'], mode='single')

    def test_from_node_1d(self):
        da = data_array(ndim=2)
        Slicer(Node(da), mode='single')

    def test_mixing_raw_data_and_nodes(self):
        a = data_array(ndim=2)
        b = 6.7 * a
        Slicer({'a': Node(a), 'b': Node(b)}, mode='single')
        Slicer({'a': a, 'b': Node(b)}, mode='single')
        Slicer({'a': Node(a), 'b': b}, mode='single')

    def test_raises_when_requested_keep_dims_do_not_exist(self):
        da = data_array(ndim=3)
        with pytest.raises(
            ValueError,
            match='Slicer plot: one or more of the requested dims to be kept',
        ):
            Slicer(da, keep=['time'], mode='single')

    def test_raises_when_number_of_keep_dims_requested_is_bad(self):
        da = data_array(ndim=4)
        with pytest.raises(
            ValueError,
            match='Slicer plot: the number of dims to be kept must be 1 or 2',
        ):
            Slicer(da, keep=['xx', 'yy', 'zz'], mode='single')
        with pytest.raises(
            ValueError, match='Slicer plot: the list of dims to be kept cannot be empty'
        ):
            Slicer(da, keep=[], mode='single')

    def test_bounds_text_boxes(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='range')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        sl.slider.controls['yy'].bound_min.value = 12
        assert sl.slider.value == {'zz': (0, 29), 'yy': (12, 39)}
        sl.slider.controls['yy'].bound_max.value = 20
        assert sl.slider.value == {'zz': (0, 29), 'yy': (12, 20)}
        # Check that entered value snaps to nearest integer
        sl.slider.controls['yy'].bound_min.value = 13.3
        assert sl.slider.value == {'zz': (0, 29), 'yy': (13, 20)}
        sl.slider.controls['yy'].bound_max.value = 18.7
        assert sl.slider.value == {'zz': (0, 29), 'yy': (13, 19)}


@pytest.mark.usefixtures("_parametrize_interactive_2d_backends")
class TestSlicer2d:
    def test_creation_keep_two_dims_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='single')
        assert sl.slider.value == {'zz': 14}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 14])

    def test_update_keep_two_dims_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='single')
        assert sl.slider.value == {'zz': 14}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 14])
        sl.slider.controls['zz'].value = 5
        assert sl.slider.value == {'zz': 5}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 5])

    def test_creation_keep_two_dims_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='range')
        assert sl.slider.value == {'zz': (0, 29)}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['zz', 0:30].sum('zz'),
        )

    def test_update_keep_two_dims_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='range')
        assert sl.slider.value == {'zz': (0, 29)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 0:30])
        sl.slider.controls['zz'].value = (5, 15)
        assert sl.slider.value == {'zz': (5, 15)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 5:16])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['zz', 5:16].sum('zz'),
        )

    def test_creation_keep_two_dims_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29)}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['zz', 0:30].sum('zz'),
        )
        # now switch to single mode
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (14, 14)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 14:15])

    def test_update_keep_two_dims_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 0:30])
        sl.slider.controls['zz'].value = (5, 15)
        assert sl.slider.value == {'zz': (5, 15)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 5:16])
        assert_allclose(
            sl.reduce_nodes[0].request_data(),
            da['zz', 5:16].sum('zz'),
        )
        # now switch to single mode
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (10, 10)}
        assert_identical(sl.slice_nodes[0].request_data(), da['zz', 10:11])

    def test_from_node_2d(self):
        da = data_array(ndim=3)
        Slicer(Node(da), mode='single')

    def test_update_triggers_autoscale(self):
        da = sc.DataArray(
            data=sc.arange('x', 5 * 10 * 20).fold(
                dim='x', sizes={'z': 20, 'y': 10, 'x': 5}
            )
        )
        # `autoscale=True` should be the default, but there is no guarantee that it will
        # not change in the future, so we explicitly set it here to make the test
        # robust.
        sl = Slicer(da, keep=['y', 'x'], autoscale=True, mode='single')
        cm = sl.figure.view.colormapper
        # Colormapper fits to the values in the initial slice (slider value in the
        # middle)
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1
        sl.slider.controls['z'].value = 6
        # Colormapper range fits to the values in the new slice
        assert cm.vmin == 5 * 10 * 6
        assert cm.vmax == 5 * 10 * 7 - 1

    def test_no_autoscale(self):
        da = sc.DataArray(
            data=sc.arange('x', 5 * 10 * 20).fold(
                dim='x', sizes={'z': 20, 'y': 10, 'x': 5}
            )
        )
        sl = Slicer(da, keep=['y', 'x'], autoscale=False, mode='single')
        cm = sl.figure.view.colormapper
        # Colormapper fits to the values in the initial slice (slider value in the
        # middle)
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1
        sl.slider.controls['z'].value = 6
        # Colormapper range does not change
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1

    def test_bounds_text_boxes(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='range')
        assert sl.slider.value == {'zz': (0, 29)}
        sl.slider.controls['zz'].bound_min.value = 12
        assert sl.slider.value == {'zz': (12, 29)}
        sl.slider.controls['zz'].bound_max.value = 20
        assert sl.slider.value == {'zz': (12, 20)}
        # Check that entered value snaps to nearest integer
        sl.slider.controls['zz'].bound_min.value = 13.3
        assert sl.slider.value == {'zz': (13, 20)}
        sl.slider.controls['zz'].bound_max.value = 18.7
        assert sl.slider.value == {'zz': (13, 19)}

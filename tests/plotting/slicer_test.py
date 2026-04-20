# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc
from scipp.testing import assert_allclose, assert_identical

from plopp import Node
from plopp.data.testing import data_array, dataset
from plopp.plotting.slicer_plot import Slicer, SlicerPlot


@pytest.mark.usefixtures("_parametrize_interactive_1d_backends")
class TestSlicer1d:
    def test_creation_keep_one_dim_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='single')
        assert sl.slider.value == {'zz': 14, 'yy': 19}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['yy', 19]['zz', 14])

    def test_update_keep_one_dim_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='single')
        assert sl.slider.value == {'zz': 14, 'yy': 19}
        assert_identical(sl.slice_nodes[0](), da['yy', 19]['zz', 14])
        sl.slider.controls['yy'].value = 5
        assert sl.slider.value == {'zz': 14, 'yy': 5}
        assert_identical(sl.slice_nodes[0](), da['yy', 5]['zz', 14])
        sl.slider.controls['zz'].value = 8
        assert sl.slider.value == {'zz': 8, 'yy': 5}
        assert_identical(sl.slice_nodes[0](), da['yy', 5]['zz', 8])

    def test_creation_keep_one_dim_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='range')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['yy', 0:40]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['yy', 0:40]['zz', 0:30].sum(['yy', 'zz']),
        )

    def test_update_keep_one_dim_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='range')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert_identical(sl.slice_nodes[0](), da['yy', 0:40]['zz', 0:30])
        sl.slider.controls['yy'].value = (5, 15)
        assert sl.slider.value == {'zz': (0, 29), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0](), da['yy', 5:16]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['yy', 5:16]['zz', 0:30].sum(['yy', 'zz']),
        )
        sl.slider.controls['zz'].value = (10, 20)
        assert sl.slider.value == {'zz': (10, 20), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0](), da['yy', 5:16]['zz', 10:21])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['yy', 5:16]['zz', 10:21].sum(['yy', 'zz']),
        )

    def test_creation_keep_one_dim_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert sl.slider.controls['yy'].slider.max == da.sizes['yy'] - 1
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['yy', 0:40]['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['yy', 0:40]['zz', 0:30].sum(['yy', 'zz']),
        )
        # now switch to single mode
        sl.slider.controls['yy'].slider_toggler.value = "-o-"
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (14, 14), 'yy': (19, 19)}
        assert_identical(sl.slice_nodes[0](), da['yy', 19:20]['zz', 14:15])

    def test_update_keep_one_dim_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29), 'yy': (0, 39)}
        assert_identical(sl.slice_nodes[0](), da['yy', 0:40]['zz', 0:30])
        sl.slider.controls['yy'].value = (5, 15)
        sl.slider.controls['zz'].value = (10, 20)
        assert sl.slider.value == {'zz': (10, 20), 'yy': (5, 15)}
        assert_identical(sl.slice_nodes[0](), da['yy', 5:16]['zz', 10:21])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['yy', 5:16]['zz', 10:21].sum(['yy', 'zz']),
        )
        # now switch to single mode
        sl.slider.controls['yy'].slider_toggler.value = "-o-"
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        sl.slider.controls['yy'].value = (4, 4)
        sl.slider.controls['zz'].value = (11, 11)
        assert sl.slider.value == {'zz': (11, 11), 'yy': (4, 4)}
        assert_identical(sl.slice_nodes[0](), da['yy', 4:5]['zz', 11:12])

    def test_no_keep(self):
        da = data_array(ndim=2)
        sl = Slicer(da)
        assert 'yy' in sl.slider.controls

    def test_no_keep_with_figure(self):
        da = data_array(ndim=2)
        sp = SlicerPlot(da)
        assert 'yy' in sp.slicer.slider.controls

    def test_with_dataset(self):
        ds = dataset(ndim=2)
        sl = Slicer(ds, keep=['xx'], mode='single')
        nodes = sl.output
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), ds['a']['yy', 5])
        assert_identical(nodes[1](), ds['b']['yy', 5])

    def test_with_dataset_with_figure(self):
        ds = dataset(ndim=2)
        sp = SlicerPlot(ds, keep=['xx'], mode='single')
        nodes = list(sp.figure.graph_nodes.values())
        sp.slicer.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), ds['a']['yy', 5])
        assert_identical(nodes[1](), ds['b']['yy', 5])

    def test_with_data_group(self):
        da = data_array(ndim=2)
        dg = sc.DataGroup(a=da, b=da * 2.5)
        sl = Slicer(dg, keep=['xx'], mode='single')
        nodes = sl.output
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), dg['a']['yy', 5])
        assert_identical(nodes[1](), dg['b']['yy', 5])

    def test_with_data_group_with_figure(self):
        da = data_array(ndim=2)
        dg = sc.DataGroup(a=da, b=da * 2.5)
        sp = SlicerPlot(dg, keep=['xx'], mode='single')
        nodes = list(sp.figure.graph_nodes.values())
        sp.slicer.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), dg['a']['yy', 5])
        assert_identical(nodes[1](), dg['b']['yy', 5])

    def test_with_dict_of_data_arrays(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        sl = Slicer({'a': a, 'b': b}, keep=['xx'], mode='single')
        nodes = sl.output
        sl.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), a['yy', 5])
        assert_identical(nodes[1](), b['yy', 5])

    def test_with_dict_of_data_arrays_with_figure(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        sp = SlicerPlot({'a': a, 'b': b}, keep=['xx'], mode='single')
        nodes = list(sp.figure.graph_nodes.values())
        sp.slicer.slider.controls['yy'].value = 5
        assert_identical(nodes[0](), a['yy', 5])
        assert_identical(nodes[1](), b['yy', 5])

    def test_with_data_arrays_same_shape_different_coord(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        b.coords['xx'] *= 1.5
        SlicerPlot({'a': a, 'b': b}, keep=['xx'], mode='single')

    def test_with_data_arrays_different_shape_along_keep_dim(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        SlicerPlot({'a': a, 'b': b['xx', :10]}, keep=['xx'], mode='single')

    def test_with_data_arrays_different_shape_along_non_keep_dim_raises(self):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        with pytest.raises(ValueError, match="Slicer plot: cannot slice dim 'yy'"):
            SlicerPlot({'a': a, 'b': b['yy', :10]}, keep=['xx'], mode='single')

    def test_with_data_arrays_same_shape_different_coords_along_non_keep_dim_raises(
        self,
    ):
        a = data_array(ndim=2)
        b = data_array(ndim=2) * 2.5
        b.coords['yy'] *= 1.5
        with pytest.raises(ValueError, match="Slicer plot: cannot slice dim 'yy'"):
            SlicerPlot({'a': a, 'b': b}, keep=['xx'], mode='single')

    def test_raises_ValueError_when_given_binned_data(self):
        da = sc.data.table_xyz(100).bin(x=10, y=20)
        with pytest.raises(ValueError, match='Cannot plot binned data'):
            SlicerPlot(da, keep=['xx'], mode='single')

    def test_from_node_1d(self):
        da = data_array(ndim=2)
        SlicerPlot(Node(da), mode='single')

    def test_mixing_raw_data_and_nodes(self):
        a = data_array(ndim=2)
        b = 6.7 * a
        SlicerPlot({'a': Node(a), 'b': Node(b)}, mode='single')
        SlicerPlot({'a': a, 'b': Node(b)}, mode='single')
        SlicerPlot({'a': Node(a), 'b': b}, mode='single')

    def test_raises_when_requested_keep_dims_do_not_exist(self):
        da = data_array(ndim=3)
        with pytest.raises(
            ValueError,
            match='Slicer plot: one or more of the requested dims to be kept',
        ):
            SlicerPlot(da, keep=['time'], mode='single')

    def test_raises_when_number_of_keep_dims_requested_is_bad(self):
        da = data_array(ndim=4)
        with pytest.raises(
            ValueError,
            match='Slicer plot: the number of dims to be kept must be 1 or 2',
        ):
            SlicerPlot(da, keep=['xx', 'yy', 'zz'], mode='single')
        with pytest.raises(
            ValueError, match='Slicer plot: the list of dims to be kept cannot be empty'
        ):
            SlicerPlot(da, keep=[], mode='single')

    def test_create_with_non_dimension_coord(self):
        da = data_array(ndim=3)
        da = da.assign_coords(x_alt=da.coords['xx'] * 2).drop_coords('xx')
        SlicerPlot(da, keep=['x_alt'], mode='single', coords=['x_alt'])


@pytest.mark.usefixtures("_parametrize_interactive_2d_backends")
class TestSlicer2d:
    @pytest.mark.parametrize("binedges", [False, True])
    @pytest.mark.parametrize("datetime", [False, True])
    def test_creation_keep_two_dims_single_mode(self, binedges, datetime):
        da = data_array(ndim=3, binedges=binedges)
        if datetime:
            da.coords['zz'] = sc.arange(
                'zz',
                sc.datetime('2022-02-20T04:32:00'),
                sc.datetime(f'2022-02-20T04:32:{da.sizes["zz"]}'),
            )
        sl = Slicer(da, keep=['xx', 'yy'], mode='single')
        assert sl.slider.value == {'zz': 14}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['zz', 14])

    def test_update_keep_two_dims_single_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='single')
        assert sl.slider.value == {'zz': 14}
        assert_identical(sl.slice_nodes[0](), da['zz', 14])
        sl.slider.controls['zz'].value = 5
        assert sl.slider.value == {'zz': 5}
        assert_identical(sl.slice_nodes[0](), da['zz', 5])

    @pytest.mark.parametrize("binedges", [False, True])
    @pytest.mark.parametrize("datetime", [False, True])
    def test_creation_keep_two_dims_range_mode(self, binedges, datetime):
        da = data_array(ndim=3, binedges=binedges)
        if datetime:
            da.coords['zz'] = sc.arange(
                'zz',
                sc.datetime('2022-02-20T04:32:00'),
                sc.datetime(f'2022-02-20T04:32:{da.sizes["zz"]}'),
            )
        sl = Slicer(da, keep=['xx', 'yy'], mode='range')
        assert sl.slider.value == {'zz': (0, 29)}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['zz', 0:30].sum('zz'),
        )

    def test_update_keep_two_dims_range_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='range')
        assert sl.slider.value == {'zz': (0, 29)}
        assert_identical(sl.slice_nodes[0](), da['zz', 0:30])
        sl.slider.controls['zz'].value = (5, 15)
        assert sl.slider.value == {'zz': (5, 15)}
        assert_identical(sl.slice_nodes[0](), da['zz', 5:16])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['zz', 5:16].sum('zz'),
        )

    @pytest.mark.parametrize("binedges", [False, True])
    @pytest.mark.parametrize("datetime", [False, True])
    def test_creation_keep_two_dims_combined_mode(self, binedges, datetime):
        da = data_array(ndim=3, binedges=binedges)
        if datetime:
            da.coords['zz'] = sc.arange(
                'zz',
                sc.datetime('2022-02-20T04:32:00'),
                sc.datetime(f'2022-02-20T04:32:{da.sizes["zz"]}'),
            )
        sl = Slicer(da, keep=['xx', 'yy'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29)}
        assert sl.slider.controls['zz'].slider.max == da.sizes['zz'] - 1
        assert_identical(sl.slice_nodes[0](), da['zz', 0:30])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['zz', 0:30].sum('zz'),
        )
        # now switch to single mode
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (14, 14)}
        assert_identical(sl.slice_nodes[0](), da['zz', 14:15])

    def test_update_keep_two_dims_combined_mode(self):
        da = data_array(ndim=3)
        sl = Slicer(da, keep=['xx', 'yy'], mode='combined')
        assert sl.slider.value == {'zz': (0, 29)}
        assert_identical(sl.slice_nodes[0](), da['zz', 0:30])
        sl.slider.controls['zz'].value = (5, 15)
        assert sl.slider.value == {'zz': (5, 15)}
        assert_identical(sl.slice_nodes[0](), da['zz', 5:16])
        assert_allclose(
            sl.reduce_nodes[0](),
            da['zz', 5:16].sum('zz'),
        )
        # now switch to single mode
        sl.slider.controls['zz'].slider_toggler.value = "-o-"
        assert sl.slider.value == {'zz': (10, 10)}
        assert_identical(sl.slice_nodes[0](), da['zz', 10:11])

    def test_no_keep(self):
        da = data_array(ndim=3)
        sl = Slicer(da)
        assert 'zz' in sl.slider.controls

    def test_no_keep_with_figure(self):
        da = data_array(ndim=3)
        sp = SlicerPlot(da)
        assert 'zz' in sp.slicer.slider.controls

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
        sp = SlicerPlot(da, keep=['y', 'x'], autoscale=True, mode='single')
        cm = sp.figure.view.colormapper
        # Colormapper fits to the values in the initial slice (slider value in the
        # middle)
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1
        sp.slicer.slider.controls['z'].value = 6
        # Colormapper range fits to the values in the new slice
        assert cm.vmin == 5 * 10 * 6
        assert cm.vmax == 5 * 10 * 7 - 1

    def test_no_autoscale(self):
        da = sc.DataArray(
            data=sc.arange('x', 5 * 10 * 20).fold(
                dim='x', sizes={'z': 20, 'y': 10, 'x': 5}
            )
        )
        sp = SlicerPlot(da, keep=['y', 'x'], autoscale=False, mode='single')
        cm = sp.figure.view.colormapper
        # Colormapper fits to the values in the initial slice (slider value in the
        # middle)
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1
        sp.slicer.slider.controls['z'].value = 6
        # Colormapper range does not change
        assert cm.vmin == 5 * 10 * 9
        assert cm.vmax == 5 * 10 * 10 - 1

    def test_create_with_non_dimension_coord(self):
        da = data_array(ndim=3)
        da = da.assign_coords(
            x_alt=da.coords['xx'] * 1.1, y_alt=da.coords['yy'] * 1.1
        ).drop_coords(['xx', 'yy'])
        SlicerPlot(
            da, keep=['y_alt', 'x_alt'], mode='single', coords=['x_alt', 'y_alt']
        )

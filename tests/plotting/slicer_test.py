# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array, dataset
from plopp.plotting.slicer import Slicer


@pytest.mark.usefixtures('_use_ipympl')
def test_creation_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 0])


@pytest.mark.usefixtures('_use_ipympl')
def test_creation_keep_one_dim():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx'])
    assert sl.slider.value == {'zz': 0, 'yy': 0}
    assert sl.slider.controls['yy']['slider'].max == da.sizes['yy'] - 1
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_nodes[0].request_data(), da['yy', 0]['zz', 0])


@pytest.mark.usefixtures('_use_ipympl')
def test_update_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 0])
    sl.slider.controls['zz']['slider'].value = 5
    assert sl.slider.value == {'zz': 5}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 5])


@pytest.mark.usefixtures('_use_ipympl')
def test_update_keep_one_dim():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx'])
    assert sl.slider.value == {'zz': 0, 'yy': 0}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['yy', 0]['zz', 0])
    sl.slider.controls['yy']['slider'].value = 5
    assert sl.slider.value == {'zz': 0, 'yy': 5}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['yy', 5]['zz', 0])
    sl.slider.controls['zz']['slider'].value = 8
    assert sl.slider.value == {'zz': 8, 'yy': 5}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['yy', 5]['zz', 8])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_dataset():
    ds = dataset(ndim=2)
    sl = Slicer(ds, keep=['xx'])
    nodes = list(sl.figure.graph_nodes.values())
    sl.slider.controls['yy']['slider'].value = 5
    assert sc.identical(nodes[0].request_data(), ds['a']['yy', 5])
    assert sc.identical(nodes[1].request_data(), ds['b']['yy', 5])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_data_group():
    da = data_array(ndim=2)
    dg = sc.DataGroup(a=da, b=da * 2.5)
    sl = Slicer(dg, keep=['xx'])
    nodes = list(sl.figure.graph_nodes.values())
    sl.slider.controls['yy']['slider'].value = 5
    assert sc.identical(nodes[0].request_data(), dg['a']['yy', 5])
    assert sc.identical(nodes[1].request_data(), dg['b']['yy', 5])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_dict_of_data_arrays():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    sl = Slicer({'a': a, 'b': b}, keep=['xx'])
    nodes = list(sl.figure.graph_nodes.values())
    sl.slider.controls['yy']['slider'].value = 5
    assert sc.identical(nodes[0].request_data(), a['yy', 5])
    assert sc.identical(nodes[1].request_data(), b['yy', 5])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_data_arrays_same_shape_different_coord():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    b.coords['xx'] *= 1.5
    Slicer({'a': a, 'b': b}, keep=['xx'])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_data_arrays_different_shape_along_keep_dim():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    Slicer({'a': a, 'b': b['xx', :10]}, keep=['xx'])


@pytest.mark.usefixtures('_use_ipympl')
def test_with_data_arrays_different_shape_along_non_keep_dim_raises():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    with pytest.raises(
        ValueError, match='Slicer plot: all inputs must have the same sizes'
    ):
        Slicer({'a': a, 'b': b['yy', :10]}, keep=['xx'])


@pytest.mark.usefixtures('_use_ipympl')
def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        Slicer(da, keep=['xx'])


@pytest.mark.usefixtures('_use_ipympl')
@pytest.mark.parametrize('ndim', [2, 3])
def test_from_node(ndim):
    da = data_array(ndim=ndim)
    Slicer(Node(da))


@pytest.mark.usefixtures('_use_ipympl')
def test_mixing_raw_data_and_nodes():
    a = data_array(ndim=2)
    b = 6.7 * a
    Slicer({'a': Node(a), 'b': Node(b)})
    Slicer({'a': a, 'b': Node(b)})
    Slicer({'a': Node(a), 'b': b})


@pytest.mark.usefixtures('_use_ipympl')
def test_raises_when_requested_keep_dims_do_not_exist():
    da = data_array(ndim=3)
    with pytest.raises(
        ValueError, match='Slicer plot: one or more of the requested dims to be kept'
    ):
        Slicer(da, keep=['time'])


@pytest.mark.usefixtures('_use_ipympl')
def test_raises_when_number_of_keep_dims_requested_is_bad():
    da = data_array(ndim=4)
    with pytest.raises(
        ValueError, match='Slicer plot: the number of dims to be kept must be 1 or 2'
    ):
        Slicer(da, keep=['xx', 'yy', 'zz'])
    with pytest.raises(
        ValueError, match='Slicer plot: the list of dims to be kept cannot be empty'
    ):
        Slicer(da, keep=[])


@pytest.mark.usefixtures('_use_ipympl')
def test_autoscale_fixed():
    da = sc.DataArray(
        data=sc.arange('x', 5 * 10 * 20).fold(dim='x', sizes={'z': 20, 'y': 10, 'x': 5})
    )
    sl = Slicer(da, keep=['y', 'x'], autoscale='fixed')
    assert sl.figure._view.colormapper.vmin == 0
    assert sl.figure._view.colormapper.vmax == 5 * 10 * 20 - 1
    sl.slider.controls['z']['slider'].value = 5
    assert sl.figure._view.colormapper.vmin == 0
    assert sl.figure._view.colormapper.vmax == 5 * 10 * 20 - 1

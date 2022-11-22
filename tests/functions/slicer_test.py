# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data.testing import data_array, dataset
from plopp.functions.slicer import Slicer
import scipp as sc
import pytest


def test_creation_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 0])


def test_creation_keep_one_dim():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx'])
    assert sl.slider.value == {'zz': 0, 'yy': 0}
    assert sl.slider.controls['yy']['slider'].max == da.sizes['yy'] - 1
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_nodes[0].request_data(), da['yy', 0]['zz', 0])


def test_update_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 0])
    sl.slider.controls['zz']['slider'].value = 5
    assert sl.slider.value == {'zz': 5}
    assert sc.identical(sl.slice_nodes[0].request_data(), da['zz', 5])


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


def test_with_dataset():
    ds = dataset(ndim=2)
    sl = Slicer(ds, keep=['xx'])
    nodes = list(sl.figure.graph_nodes.values())
    sl.slider.controls['yy']['slider'].value = 5
    assert sc.identical(nodes[0].request_data(), ds['a']['yy', 5])
    assert sc.identical(nodes[1].request_data(), ds['b']['yy', 5])


def test_with_dict_of_data_arrays():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    sl = Slicer({'a': a, 'b': b}, keep=['xx'])
    nodes = list(sl.figure.graph_nodes.values())
    sl.slider.controls['yy']['slider'].value = 5
    assert sc.identical(nodes[0].request_data(), a['yy', 5])
    assert sc.identical(nodes[1].request_data(), b['yy', 5])


def test_with_mismatching_data_arrays_raises():
    a = data_array(ndim=2)
    b = data_array(ndim=2) * 2.5
    b.coords['xx'] *= 1.1
    with pytest.raises(sc.DatasetError):
        _ = Slicer({'a': a, 'b': b}, keep=['xx'])

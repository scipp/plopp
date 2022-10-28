# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import data_array
from plopp.functions.slicer import Slicer
import scipp as sc


def test_creation_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da=da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_node.request_data(), da['zz', 0])


def test_creation_keep_one_dim():
    da = data_array(ndim=3)
    sl = Slicer(da=da, keep=['xx'])
    assert sl.slider.value == {'zz': 0, 'yy': 0}
    assert sl.slider.controls['yy']['slider'].max == da.sizes['yy'] - 1
    assert sl.slider.controls['zz']['slider'].max == da.sizes['zz'] - 1
    assert sc.identical(sl.slice_node.request_data(), da['yy', 0]['zz', 0])


def test_update_keep_two_dims():
    da = data_array(ndim=3)
    sl = Slicer(da=da, keep=['xx', 'yy'])
    assert sl.slider.value == {'zz': 0}
    assert sc.identical(sl.slice_node.request_data(), da['zz', 0])
    sl.slider.controls['zz']['slider'].value = 5
    assert sl.slider.value == {'zz': 5}
    assert sc.identical(sl.slice_node.request_data(), da['zz', 5])


def test_update_keep_one_dim():
    da = data_array(ndim=3)
    sl = Slicer(da=da, keep=['xx'])
    assert sl.slider.value == {'zz': 0, 'yy': 0}
    assert sc.identical(sl.slice_node.request_data(), da['yy', 0]['zz', 0])
    sl.slider.controls['yy']['slider'].value = 5
    assert sl.slider.value == {'zz': 0, 'yy': 5}
    assert sc.identical(sl.slice_node.request_data(), da['yy', 5]['zz', 0])
    sl.slider.controls['zz']['slider'].value = 8
    assert sl.slider.value == {'zz': 8, 'yy': 5}
    assert sc.identical(sl.slice_node.request_data(), da['yy', 5]['zz', 8])

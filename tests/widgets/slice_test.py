# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.widgets import SliceWidget, slice_dims
from plopp.data import data_array
from scipp import identical


def test_slice_creation():
    da = data_array(ndim=3)
    dims = ['xx', 'yy']
    sw = SliceWidget(da, dims=dims)
    assert sw._slider_dims == dims
    assert sw.controls['xx']['slider'].min == 0
    assert sw.controls['xx']['slider'].max == da.sizes['xx'] - 1
    assert sw.controls['xx']['slider'].description == 'xx'
    assert sw.controls['yy']['slider'].min == 0
    assert sw.controls['yy']['slider'].max == da.sizes['yy'] - 1
    assert sw.controls['yy']['slider'].description == 'yy'


def test_slice_value_property():
    da = data_array(ndim=3)
    dims = ['xx', 'yy']
    sw = SliceWidget(da, dims=dims)
    sw.controls['xx']['slider'].value = 10
    sw.controls['yy']['slider'].value = 15
    assert sw.value == {'xx': 10, 'yy': 15}


def test_slice_label_updates():
    da = data_array(ndim=3)
    da.coords['xx'] *= 1.1
    da.coords['yy'] *= 3.3
    dims = ['xx', 'yy']
    sw = SliceWidget(da, dims=dims)
    assert sw.controls['xx']['label'].value == '0.0 [m]'
    sw.controls['xx']['slider'].value = 10
    assert sw.controls['xx']['label'].value == '11.0 [m]'
    assert sw.controls['yy']['label'].value == '0.0 [m]'
    sw.controls['yy']['slider'].value = 15
    assert sw.controls['yy']['label'].value == '49.5 [m]'


def test_slice_dims():
    da = data_array(ndim=3)
    slices = {'xx': 8, 'yy': 7}
    expected = da['xx', slices['xx']]['yy', slices['yy']]
    assert identical(slice_dims().func(da, slices=slices), expected)

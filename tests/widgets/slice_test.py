# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
from scipp import identical

from plopp.data.testing import data_array
from plopp.widgets import RangeSliceWidget, SliceWidget, slice_dims


@pytest.mark.parametrize("widget", [SliceWidget, RangeSliceWidget])
def test_slice_creation(widget):
    da = data_array(ndim=3)
    sw = widget(da, dims=['yy', 'xx'])
    assert sw._slider_dims == ['yy', 'xx']
    assert sw.controls['xx']['slider'].min == 0
    assert sw.controls['xx']['slider'].max == da.sizes['xx'] - 1
    assert sw.controls['xx']['slider'].description == 'xx'
    assert sw.controls['yy']['slider'].min == 0
    assert sw.controls['yy']['slider'].max == da.sizes['yy'] - 1
    assert sw.controls['yy']['slider'].description == 'yy'


def test_slice_value_property():
    da = data_array(ndim=3)
    sw = SliceWidget(da, dims=['yy', 'xx'])
    sw.controls['xx']['slider'].value = 10
    sw.controls['yy']['slider'].value = 15
    assert sw.value == {'xx': 10, 'yy': 15}


def test_slice_label_updates():
    da = data_array(ndim=3)
    da.coords['xx'] *= 1.1
    da.coords['yy'] *= 3.3
    sw = SliceWidget(da, dims=['yy', 'xx'])
    sw.controls['xx']['slider'].value = 0
    sw.controls['yy']['slider'].value = 0
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


def test_range_slice_dims():
    da = data_array(ndim=3)
    slices = {'xx': (8, 9), 'yy': (7, 10)}
    expected = da['xx', slice(*slices['xx'])]['yy', slice(*slices['yy'])]
    assert identical(slice_dims().func(da, slices=slices), expected)

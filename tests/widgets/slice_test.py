# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
from scipp import identical

from plopp.data.testing import data_array
from plopp.widgets import CombinedSliceWidget, RangeSliceWidget, SliceWidget, slice_dims


@pytest.mark.parametrize("widget", [SliceWidget, RangeSliceWidget, CombinedSliceWidget])
def test_slice_creation(widget):
    da = data_array(ndim=3)
    sw = widget(da, dims=['yy', 'xx'])
    assert set(sw.controls.keys()) == {'yy', 'xx'}
    assert sw.controls['xx'].slider.min == 0
    assert sw.controls['xx'].slider.max == da.sizes['xx'] - 1
    assert sw.controls['xx'].dim_label.value == 'xx'
    assert sw.controls['yy'].slider.min == 0
    assert sw.controls['yy'].slider.max == da.sizes['yy'] - 1
    assert sw.controls['yy'].dim_label.value == 'yy'


def test_slice_value_property():
    da = data_array(ndim=3)
    sw = SliceWidget(da, dims=['yy', 'xx'])
    sw.controls['xx'].value = 10
    sw.controls['yy'].value = 15
    assert sw.value == {'xx': 10, 'yy': 15}


def test_slice_label_updates_single_slice():
    da = data_array(ndim=3)
    da.coords['xx'] *= 1.1
    da.coords['yy'] *= 3.3
    sw = SliceWidget(da, dims=['yy', 'xx'])
    sw.controls['xx'].value = 0
    sw.controls['yy'].value = 0
    assert sw.controls['xx'].unit.value == '[m]'
    assert float(sw.controls['xx'].bounds.string_value) == 0.0
    sw.controls['xx'].value = 10
    assert float(sw.controls['xx'].bounds.string_value) == 11.0
    assert float(sw.controls['yy'].bounds.string_value) == 0.0
    sw.controls['yy'].value = 15
    assert float(sw.controls['yy'].bounds.string_value) == 49.5


def test_slice_label_updates_single_binedge_slice():
    da = data_array(ndim=3, binedges=True)
    da.coords['zz'] *= 2.2
    sw = SliceWidget(da, dims=['zz'])
    sw.controls['zz'].value = 0
    assert sw.controls['zz'].unit.value == '[m]'
    bounds = sw.controls['zz'].bounds.string_value.split(":")
    assert float(bounds[0]) == 0.0
    assert float(bounds[1]) == 2.2
    sw.controls['zz'].value = 10
    bounds = sw.controls['zz'].bounds.string_value.split(":")
    assert float(bounds[0]) == 22.0
    assert float(bounds[1]) == 24.2


def test_slice_label_updates_range_slice():
    da = data_array(ndim=3)
    da.coords['zz'] *= 2.2
    sw = RangeSliceWidget(da, dims=['zz'])
    sw.controls['zz'].value = (0, 1)
    assert sw.controls['zz'].unit.value == '[m]'
    bounds = sw.controls['zz'].bounds.string_value.split(":")
    assert float(bounds[0]) == 0.0
    assert float(bounds[1]) == 2.2
    sw.controls['zz'].value = (10, 16)
    bounds = sw.controls['zz'].bounds.string_value.split(":")
    assert float(bounds[0]) == 22.0
    assert float(bounds[1]) == 16 * 2.2


def test_make_slice_widget_with_player():
    da = data_array(ndim=3)
    sw = SliceWidget(da, dims=['zz'], enable_player=True)
    assert sw.controls['zz'].player is not None


def test_slice_dims():
    da = data_array(ndim=3)
    slices = {'xx': 8, 'yy': 7}
    expected = da['xx', slices['xx']]['yy', slices['yy']]
    assert identical(slice_dims().func(da, slices=slices), expected)


def test_range_slice_dims():
    da = data_array(ndim=3)
    slices = {'xx': (8, 9), 'yy': (7, 10)}
    # Note that we want to include the stop index in the slice
    expected = da['xx', slices['xx'][0] : slices['xx'][1] + 1][
        'yy', slices['yy'][0] : slices['yy'][1] + 1
    ]
    assert identical(slice_dims().func(da, slices=slices), expected)

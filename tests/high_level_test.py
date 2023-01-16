# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import ipywidgets as ipw
import scipp as sc

from plopp import figure1d, figure2d, input_node, node, widget_node
from plopp.data.testing import data_array, dataset
from plopp.widgets import Box, Checkboxes, SliceWidget, slice_dims


@node
def hide_masks(data_array, masks):
    out = data_array.copy(deep=False)
    for name, value in masks.items():
        if name in out.masks and (not value):
            del out.masks[name]
    return out


def test_single_1d_line():
    da = data_array(ndim=1)
    n = input_node(da)
    _ = figure1d(n)


def test_two_1d_lines():
    ds = dataset(ndim=1)
    a = input_node(ds['a'])
    b = input_node(ds['b'])
    _ = figure1d(a, b)


def test_difference_of_two_1d_lines():
    ds = dataset(ndim=1)
    a = input_node(ds['a'])
    b = input_node(ds['b'])

    @node
    def diff(x, y):
        return x - y

    c = diff(a, b)
    _ = figure1d(a, b, c)


def test_2d_image():
    da = data_array(ndim=2)
    a = input_node(da)
    _ = figure2d(a)


def test_2d_image_smoothing_slider():
    da = data_array(ndim=2)
    a = input_node(da)

    sl = ipw.IntSlider(min=1, max=10)
    sigma_node = widget_node(sl)

    try:
        from scipp.scipy.ndimage import gaussian_filter
    except ImportError:
        from scipp.ndimage import gaussian_filter
    smooth_node = node(gaussian_filter)(a, sigma=sigma_node)

    fig = figure2d(smooth_node)
    Box([fig.to_widget(), sl])
    sl.value = 5


def test_2d_image_with_masks():
    da = data_array(ndim=2)
    da.masks['m1'] = da.data < sc.scalar(0.0, unit='m/s')
    da.masks['m2'] = da.coords['xx'] > sc.scalar(30., unit='m')

    a = input_node(da)

    widget = Checkboxes(da.masks.keys())
    w = widget_node(widget)

    masks_node = hide_masks(a, w)
    fig = figure2d(masks_node)
    Box([fig.to_widget(), widget])
    widget.toggle_all_button.value = False


def test_two_1d_lines_with_masks():
    ds = dataset()
    ds['a'].masks['m1'] = ds['a'].coords['xx'] > sc.scalar(40.0, unit='m')
    ds['a'].masks['m2'] = ds['a'].data < ds['b'].data
    ds['b'].masks['m1'] = ds['b'].coords['xx'] < sc.scalar(5.0, unit='m')

    a = input_node(ds['a'])
    b = input_node(ds['b'])

    widget = Checkboxes(list(ds['a'].masks.keys()) + list(ds['b'].masks.keys()))
    w = widget_node(widget)

    node_masks_a = hide_masks(a, w)
    node_masks_b = hide_masks(b, w)
    fig = figure1d(node_masks_a, node_masks_b)
    Box([fig.to_widget(), widget])
    widget.toggle_all_button.value = False


def test_node_sum_data_along_y():
    da = data_array(ndim=2, binedges=True)
    a = input_node(da)

    s = node(sc.sum, dim='yy')(a)

    fig1 = figure2d(a)
    fig2 = figure1d(s)
    Box([[fig1.to_widget(), fig2.to_widget()]])


def test_slice_3d_cube():
    da = data_array(ndim=3)
    a = input_node(da)
    sl = SliceWidget(sizes={'zz': da.sizes['zz']}, coords=da.coords)
    w = widget_node(sl)

    slice_node = slice_dims(a, w)

    fig = figure2d(slice_node)
    Box([fig.to_widget(), sl])
    sl.controls["zz"]["slider"].value = 10


def test_3d_image_slicer_with_connected_side_histograms():
    da = data_array(ndim=3)
    a = input_node(da)
    sl = SliceWidget(sizes={'zz': da.sizes['zz']}, coords=da.coords)
    w = widget_node(sl)

    sliced = slice_dims(a, w)
    fig = figure2d(sliced)

    histx = node(sc.sum, dim='xx')(sliced)
    histy = node(sc.sum, dim='yy')(sliced)

    fx = figure1d(histx)
    fy = figure1d(histy)
    Box([[fx.to_widget(), fy.to_widget()], fig.to_widget(), sl])
    sl.controls["zz"]["slider"].value = 10

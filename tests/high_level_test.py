# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import ipywidgets as ipw
import pytest
import scipp as sc

from plopp import Node, imagefigure, linefigure, node, widget_node
from plopp.data.testing import data_array, dataset
from plopp.widgets import Box, Checkboxes, SliceWidget, slice_dims


@node
def hide_masks(data_array, masks):
    out = data_array.copy(deep=False)
    for name, value in masks.items():
        if name in out.masks and (not value):
            del out.masks[name]
    return out


@pytest.mark.usefixtures("_parametrize_all_backends")
class TestHighLevel1d:
    def test_single_1d_line(self):
        da = data_array(ndim=1)
        n = Node(da)
        _ = linefigure(n)

    def test_two_1d_lines(self):
        ds = dataset(ndim=1)
        a = Node(ds['a'])
        b = Node(ds['b'])
        _ = linefigure(a, b)

    def test_difference_of_two_1d_lines(self):
        ds = dataset(ndim=1)
        a = Node(ds['a'])
        b = Node(ds['b'])

        @node
        def diff(x, y):
            return x - y

        c = diff(a, b)
        _ = linefigure(a, b, c)


@pytest.mark.usefixtures("_parametrize_mpl_backends")
class TestHighLevel2d:
    def test_2d_image(self):
        da = data_array(ndim=2)
        a = Node(da)
        _ = imagefigure(a)


@pytest.mark.usefixtures("_parametrize_interactive_2d_backends")
class TestHighLevelInteractive:
    def test_2d_image_smoothing_slider(self):
        da = data_array(ndim=2)
        a = Node(da)

        sl = ipw.IntSlider(min=1, max=10)
        sigma_node = widget_node(sl)

        from scipp.scipy.ndimage import gaussian_filter

        smooth_node = Node(gaussian_filter, a, sigma=sigma_node)

        fig = imagefigure(smooth_node)
        Box([fig, sl])
        sl.value = 5

    def test_2d_image_with_masks(self):
        da = data_array(ndim=2)
        da.masks['m1'] = da.data < sc.scalar(0.0, unit='m/s')
        da.masks['m2'] = da.coords['xx'] > sc.scalar(30.0, unit='m')

        a = Node(da)

        widget = Checkboxes(da.masks.keys())
        w = widget_node(widget)

        masks_node = hide_masks(a, w)
        fig = imagefigure(masks_node)
        Box([fig, widget])
        widget.toggle_all_button.value = False

    def test_two_1d_lines_with_masks(self):
        ds = dataset()
        ds['a'].masks['m1'] = ds['a'].coords['xx'] > sc.scalar(40.0, unit='m')
        ds['a'].masks['m2'] = ds['a'].data < ds['b'].data
        ds['b'].masks['m1'] = ds['b'].coords['xx'] < sc.scalar(5.0, unit='m')

        a = Node(ds['a'])
        b = Node(ds['b'])

        widget = Checkboxes(list(ds['a'].masks.keys()) + list(ds['b'].masks.keys()))
        w = widget_node(widget)

        node_masks_a = hide_masks(a, w)
        node_masks_b = hide_masks(b, w)
        fig = linefigure(node_masks_a, node_masks_b)
        Box([fig, widget])
        widget.toggle_all_button.value = False

    def test_node_sum_data_along_y(self):
        da = data_array(ndim=2, binedges=True)
        a = Node(da)
        s = Node(sc.sum, a, dim='yy')

        fig1 = imagefigure(a)
        fig2 = linefigure(s)
        Box([[fig1, fig2]])

    def test_slice_3d_cube(self):
        da = data_array(ndim=3)
        a = Node(da)
        sl = SliceWidget(da, dims=['zz'])
        w = widget_node(sl)

        slice_node = slice_dims(a, w)

        fig = imagefigure(slice_node)
        Box([fig, sl])
        sl.controls["zz"].value = 10

    def test_3d_image_slicer_with_connected_side_histograms(self):
        da = data_array(ndim=3)
        a = Node(da)
        sl = SliceWidget(da, dims=['zz'])
        w = widget_node(sl)

        sliced = slice_dims(a, w)
        fig = imagefigure(sliced)

        histx = Node(sc.sum, sliced, dim='xx')
        histy = Node(sc.sum, sliced, dim='yy')

        fx = linefigure(histx)
        fy = linefigure(histy)
        Box([[fx, fy], fig, sl])
        sl.controls["zz"].value = 10

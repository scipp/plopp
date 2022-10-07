# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.scatterfig import ScatterFig
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc


def test_creation():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    key = list(fig._children.keys())[0]
    assert isinstance(fig._children[key], PointCloud)
    assert sc.identical(fig._children[key]._data, da)
    assert fig.outline is not None


def test_update():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    key = list(fig._children.keys())[0]
    fig.update(da * 3.3, key=key)
    assert sc.identical(fig._children[key]._data, da * 3.3)


def test_toggle_outline():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert fig.outline.visible
    fig.toggle_outline()
    assert not fig.outline.visible
    fig.toggle_outline()
    assert fig.outline.visible


def test_show_hide_cuts():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    fig.cut_x.button.value = True
    assert len(fig._children) == 2
    fig.cut_y.button.value = True
    assert len(fig._children) == 3
    fig.cut_z.button.value = True
    assert len(fig._children) == 4
    fig.cut_x.button.value = False
    assert len(fig._children) == 3
    fig.cut_y.button.value = False
    assert len(fig._children) == 2
    fig.cut_z.button.value = False
    assert len(fig._children) == 1


def test_move_cut():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    fig.cut_x.button.value = True
    assert fig.cut_x.outline.position[0] == fig.cut_x.slider.value
    pts = list(fig._children.values())[-1]
    npoints = pts.geometry.attributes['position'].array.shape[0]
    fig.cut_x.slider.value = -5.0
    assert fig.cut_x.outline.position[0] == fig.cut_x.slider.value
    new_pts = list(fig._children.values())[-1]
    assert npoints != new_pts.geometry.attributes['position'].array.shape[0]


def test_cut_thickness():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    fig.cut_x.button.value = True
    pts = list(fig._children.values())[-1]
    npoints = pts.geometry.attributes['position'].array.shape[0]
    fig.cut_x.button_plus.click()
    new_pts = list(fig._children.values())[-1]
    assert npoints < new_pts.geometry.attributes['position'].array.shape[0]
    fig.cut_x.button_minus.click()
    new_pts = list(fig._children.values())[-1]
    assert npoints == new_pts.geometry.attributes['position'].array.shape[0]
    fig.cut_x.button_minus.click()
    new_pts = list(fig._children.values())[-1]
    assert npoints > new_pts.geometry.attributes['position'].array.shape[0]


def test_empty_cut():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    fig.cut_y.button.value = True
    assert len(fig._children) == 2
    fig.cut_y.slider.value = 34.0  # This cut should contain no points
    assert len(fig._children) == 1

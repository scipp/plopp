# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.fig3d import Figure3d
from plopp.widgets import TriCutTool
from plopp import input_node


def test_show_hide_cuts():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    tri = TriCutTool(fig)
    assert len(fig.artists) == 1
    tri.cut_x.button.value = True
    assert len(fig.artists) == 2
    tri.cut_y.button.value = True
    assert len(fig.artists) == 3
    tri.cut_z.button.value = True
    assert len(fig.artists) == 4
    tri.cut_x.button.value = False
    assert len(fig.artists) == 3
    tri.cut_y.button.value = False
    assert len(fig.artists) == 2
    tri.cut_z.button.value = False
    assert len(fig.artists) == 1


def test_move_cut():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    tri = TriCutTool(fig)
    tri.cut_x.button.value = True
    assert tri.cut_x.outline.position[0] == tri.cut_x.slider.value
    pts = list(fig.artists.values())[-1]
    npoints = pts.geometry.attributes['position'].array.shape[0]
    tri.cut_x.slider.value = -5.0
    assert tri.cut_x.outline.position[0] == tri.cut_x.slider.value
    new_pts = list(fig.artists.values())[-1]
    assert npoints != new_pts.geometry.attributes['position'].array.shape[0]


def test_cut_thickness():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    tri = TriCutTool(fig)
    tri.cut_x.button.value = True
    pts = list(fig.artists.values())[-1]
    npoints = pts.geometry.attributes['position'].array.shape[0]
    tri.cut_x.button_plus.click()
    new_pts = list(fig.artists.values())[-1]
    assert npoints < new_pts.geometry.attributes['position'].array.shape[0]
    tri.cut_x.button_minus.click()
    new_pts = list(fig.artists.values())[-1]
    assert npoints == new_pts.geometry.attributes['position'].array.shape[0]
    tri.cut_x.button_minus.click()
    new_pts = list(fig.artists.values())[-1]
    assert npoints > new_pts.geometry.attributes['position'].array.shape[0]


def test_empty_cut():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    tri = TriCutTool(fig)
    assert len(fig.artists) == 1
    tri.cut_y.button.value = True
    assert len(fig.artists) == 2
    tri.cut_y.slider.value = 34.0  # This cut should contain no points
    assert len(fig.artists) == 1

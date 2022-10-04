# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.fig3d import Fig3d
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc
from copy import copy


def test_creation():
    fig = Fig3d(figsize=(700, 450))
    assert len(fig._children) == 0
    assert fig.renderer.width == 700
    assert fig.renderer.height == 450
    assert all(
        [fig.camera, fig.scene, fig.controls, fig.renderer, fig.toolbar, fig.axes_3d])
    assert fig.outline is None


def test_update_with_point_cloud():
    fig = Fig3d(x='x', y='y', z='z')
    assert len(fig._children) == 0
    da = scatter_data()
    key = 'scatter'
    fig.update(da, key=key)
    assert isinstance(fig._children[key], PointCloud)
    assert sc.identical(fig._children[key]._data, da)
    assert fig.outline is not None


def test_create_with_node():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    child = list(fig._children.values())[0]
    assert isinstance(child, PointCloud)
    assert sc.identical(child._data, da)
    assert fig.outline is not None


def test_camera_home():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    original = copy(fig.camera.position)
    fig.camera.position = [10, 20, 30]
    fig.home()
    assert fig.camera.position == original


def test_camera_x():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    center = copy(fig.camera_backup["center"])
    fig.camera.position = [10, 20, 30]
    fig.camera_x_normal()
    assert fig.camera.position[0] < center[0]
    assert fig.camera.position[1] == center[1]
    assert fig.camera.position[2] == center[2]
    fig.camera_x_normal()
    assert fig.camera.position[0] > center[0]
    assert fig.camera.position[1] == center[1]
    assert fig.camera.position[2] == center[2]


def test_camera_y():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    center = copy(fig.camera_backup["center"])
    fig.camera.position = [10, 20, 30]
    fig.camera_y_normal()
    assert fig.camera.position[0] == center[0]
    assert fig.camera.position[1] < center[1]
    assert fig.camera.position[2] == center[2]
    fig.camera_y_normal()
    assert fig.camera.position[0] == center[0]
    assert fig.camera.position[1] > center[1]
    assert fig.camera.position[2] == center[2]


def test_camera_z():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    center = copy(fig.camera_backup["center"])
    fig.camera.position = [10, 20, 30]
    fig.camera_z_normal()
    assert fig.camera.position[0] == center[0]
    assert fig.camera.position[1] == center[1]
    assert fig.camera.position[2] < center[2]
    fig.camera_z_normal()
    assert fig.camera.position[0] == center[0]
    assert fig.camera.position[1] == center[1]
    assert fig.camera.position[2] > center[2]


def test_toggle_outline():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    assert fig.outline.visible
    fig.toggle_outline()
    assert not fig.outline.visible
    fig.toggle_outline()
    assert fig.outline.visible


def test_toggle_axes_3d():
    da = scatter_data()
    fig = Fig3d(input_node(da), x='x', y='y', z='z')
    assert fig.axes_3d.visible
    fig.toggle_axes3d()
    assert not fig.axes_3d.visible
    fig.toggle_axes3d()
    assert fig.axes_3d.visible

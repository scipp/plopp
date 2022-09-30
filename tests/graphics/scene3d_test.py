# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.scene3d import Scene3d
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc
from copy import copy


def test_creation():
    scene = Scene3d(figsize=(700, 450))
    assert len(scene._children) == 0
    assert scene.renderer.width == 700
    assert scene.renderer.height == 450
    assert all([
        scene.camera, scene.scene, scene.controls, scene.renderer, scene.toolbar,
        scene.axes_3d
    ])
    assert scene.outline is None


def test_update_with_point_cloud():
    scene = Scene3d(x='x', y='y', z='z')
    assert len(scene._children) == 0
    da = scatter_data()
    key = 'scatter'
    scene.update(da, key=key)
    assert isinstance(scene._children[key], PointCloud)
    assert sc.identical(scene._children[key]._data, da)
    assert scene.outline is not None


def test_create_with_node():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    assert len(scene._children) == 1
    child = list(scene._children.values())[0]
    assert isinstance(child, PointCloud)
    assert sc.identical(child._data, da)
    assert scene.outline is not None


def test_camera_home():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    original = copy(scene.camera.position)
    scene.camera.position = [10, 20, 30]
    scene.home()
    assert scene.camera.position == original


def test_camera_x():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    center = copy(scene.camera_backup["center"])
    scene.camera.position = [10, 20, 30]
    scene.camera_x_normal()
    assert scene.camera.position[0] < center[0]
    assert scene.camera.position[1] == center[1]
    assert scene.camera.position[2] == center[2]
    scene.camera_x_normal()
    assert scene.camera.position[0] > center[0]
    assert scene.camera.position[1] == center[1]
    assert scene.camera.position[2] == center[2]


def test_camera_y():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    center = copy(scene.camera_backup["center"])
    scene.camera.position = [10, 20, 30]
    scene.camera_y_normal()
    assert scene.camera.position[0] == center[0]
    assert scene.camera.position[1] < center[1]
    assert scene.camera.position[2] == center[2]
    scene.camera_y_normal()
    assert scene.camera.position[0] == center[0]
    assert scene.camera.position[1] > center[1]
    assert scene.camera.position[2] == center[2]


def test_camera_z():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    center = copy(scene.camera_backup["center"])
    scene.camera.position = [10, 20, 30]
    scene.camera_z_normal()
    assert scene.camera.position[0] == center[0]
    assert scene.camera.position[1] == center[1]
    assert scene.camera.position[2] < center[2]
    scene.camera_z_normal()
    assert scene.camera.position[0] == center[0]
    assert scene.camera.position[1] == center[1]
    assert scene.camera.position[2] > center[2]


def test_toggle_outline():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    assert scene.outline.visible
    scene.toggle_outline()
    assert not scene.outline.visible
    scene.toggle_outline()
    assert scene.outline.visible


def test_toggle_axes_3d():
    da = scatter_data()
    scene = Scene3d(input_node(da), x='x', y='y', z='z')
    assert scene.axes_3d.visible
    scene.toggle_axes3d()
    assert not scene.axes_3d.visible
    scene.toggle_axes3d()
    assert scene.axes_3d.visible

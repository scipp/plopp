# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.graphics.fig3d import Fig3d
import scipp as sc
from copy import copy


def _make_limits():
    return (sc.array(dims=['x'], values=[1.5, 3.5],
                     unit='m'), sc.array(dims=['y'], values=[-5.0, 5.0], unit='m'),
            sc.array(dims=['z'], values=[-0.1, 17.0], unit='m'))


def test_creation():
    fig = Fig3d(figsize=(700, 450))
    assert len(fig._children) == 0
    assert fig.renderer.width == 700
    assert fig.renderer.height == 450
    assert all(
        [fig.camera, fig.scene, fig.controls, fig.renderer, fig.toolbar, fig.axes_3d])
    assert fig.outline is None


def test_camera_home():
    fig = Fig3d()
    fig._update_camera(limits=_make_limits())
    original = copy(fig.camera.position)
    fig.camera.position = [10, 20, 30]
    fig.home()
    assert fig.camera.position == original


def test_camera_x():
    fig = Fig3d()
    fig._update_camera(limits=_make_limits())
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
    fig = Fig3d()
    fig._update_camera(limits=_make_limits())
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
    fig = Fig3d()
    fig._update_camera(limits=_make_limits())
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


def test_toggle_axes_3d():
    fig = Fig3d()
    assert fig.axes_3d.visible
    fig.toggle_axes3d()
    assert not fig.axes_3d.visible
    fig.toggle_axes3d()
    assert fig.axes_3d.visible

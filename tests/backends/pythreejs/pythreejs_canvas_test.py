# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from copy import copy

import pytest
import scipp as sc

from plopp import Camera
from plopp.backends.pythreejs.canvas import Canvas
from plopp.backends.pythreejs.outline import Outline


def _make_limits():
    return (
        sc.array(dims=['x'], values=[1.5, 3.5], unit='m'),
        sc.array(dims=['y'], values=[-5.0, 5.0], unit='m'),
        sc.array(dims=['z'], values=[-0.1, 17.0], unit='m'),
    )


def _assert_pos(expected, canvas, key):
    assert (
        expected == canvas.camera.position
        if key == 'position'
        else canvas.controls.target
    )


def test_creation():
    canvas = Canvas(figsize=(700, 450))
    assert canvas.renderer.width == 700
    assert canvas.renderer.height == 450
    assert all(
        [canvas.camera, canvas.scene, canvas.controls, canvas.renderer, canvas.axes_3d]
    )
    assert canvas.outline is None


def test_make_outline():
    canvas = Canvas()
    assert canvas.outline is None
    canvas.make_outline(limits=_make_limits())
    assert isinstance(canvas.outline, Outline)
    assert canvas.outline.visible


def test_camera_home():
    canvas = Canvas()
    canvas._update_camera(limits=_make_limits())
    original = copy(canvas.camera.position)
    canvas.camera.position = [10, 20, 30]
    canvas.home()
    assert canvas.camera.position == original


def test_camera_x():
    canvas = Canvas()
    canvas._update_camera(limits=_make_limits())
    center = copy(canvas.camera_backup["center"])
    canvas.camera.position = [10, 20, 30]
    canvas.camera_x_normal()
    assert canvas.camera.position[0] < center[0]
    assert canvas.camera.position[1] == center[1]
    assert canvas.camera.position[2] == center[2]
    canvas.camera_x_normal()
    assert canvas.camera.position[0] > center[0]
    assert canvas.camera.position[1] == center[1]
    assert canvas.camera.position[2] == center[2]


def test_camera_y():
    canvas = Canvas()
    canvas._update_camera(limits=_make_limits())
    center = copy(canvas.camera_backup["center"])
    canvas.camera.position = [10, 20, 30]
    canvas.camera_y_normal()
    assert canvas.camera.position[0] == center[0]
    assert canvas.camera.position[1] < center[1]
    assert canvas.camera.position[2] == center[2]
    canvas.camera_y_normal()
    assert canvas.camera.position[0] == center[0]
    assert canvas.camera.position[1] > center[1]
    assert canvas.camera.position[2] == center[2]


def test_camera_z():
    canvas = Canvas()
    canvas._update_camera(limits=_make_limits())
    center = copy(canvas.camera_backup["center"])
    canvas.camera.position = [10, 20, 30]
    canvas.camera_z_normal()
    assert canvas.camera.position[0] == center[0]
    assert canvas.camera.position[1] == center[1]
    assert canvas.camera.position[2] < center[2]
    canvas.camera_z_normal()
    assert canvas.camera.position[0] == center[0]
    assert canvas.camera.position[1] == center[1]
    assert canvas.camera.position[2] > center[2]


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_tuple_of_floats(key):
    pos = (1.5, 22.0, -3.0)
    canvas = Canvas(camera=Camera(**{key: pos}))
    canvas._update_camera(limits=_make_limits())
    _assert_pos(pos, canvas, key)
    setattr(canvas.camera, key, (10, 20, 30))
    canvas.home()
    _assert_pos(pos, canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_vector(key):
    pos = (0, 1, 2)
    vec = sc.vector(pos, unit='m')
    canvas = Canvas(camera=Camera(**{key: vec}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    _assert_pos(pos, canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_vector_unit_conversion(key):
    vec = sc.vector([0, 1, 2], unit='cm')
    canvas = Canvas(camera=Camera(**{key: vec}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    _assert_pos((0, 0.01, 0.02), canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_vector_bad_unit_raises(key):
    vec = sc.vector([0, 1, 2], unit='s')
    canvas = Canvas(camera=Camera(**{key: vec}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    with pytest.raises(sc.UnitError):
        canvas._update_camera(limits=_make_limits())


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_vector_can_convert_a_single_field(key):
    vec = sc.vector([0, 1, 2], unit='m')
    canvas = Canvas(camera=Camera(**{key: vec}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'cm'
    canvas._update_camera(limits=_make_limits())
    _assert_pos((0, 1, 200), canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_tuple_of_variables(key):
    pos = [
        sc.scalar(2.0, unit='m'),
        sc.scalar(-12.0, unit='m'),
        sc.scalar(44.0, unit='m'),
    ]
    canvas = Canvas(camera=Camera(**{key: pos}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    _assert_pos((2.0, -12.0, 44.0), canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_tuple_of_variables_unit_conversion(key):
    pos = [
        sc.scalar(2.0, unit='m'),
        sc.scalar(-12.0, unit='cm'),
        sc.scalar(44.0, unit='mm'),
    ]
    canvas = Canvas(camera=Camera(**{key: pos}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    _assert_pos((2.0, -0.12, 0.044), canvas, key)


@pytest.mark.parametrize('key', ['position', 'look_at'])
def test_camera_user_tuple_of_variables_bad_unit_raises(key):
    pos = [
        sc.scalar(2.0, unit='m'),
        sc.scalar(-12.0, unit='m'),
        sc.scalar(44.0, unit='m'),
    ]
    canvas = Canvas(camera=Camera(**{key: pos}))
    canvas.xunit = 's'
    canvas.yunit = 's'
    canvas.zunit = 's'
    with pytest.raises(sc.UnitError):
        canvas._update_camera(limits=_make_limits())


@pytest.mark.parametrize('key', ['near', 'far'])
def test_camera_user_float(key):
    value = 6.8
    canvas = Canvas(camera=Camera(**{key: value}))
    canvas._update_camera(limits=_make_limits())
    assert getattr(canvas.camera, key) == value


@pytest.mark.parametrize('key', ['near', 'far'])
def test_camera_user_variable(key):
    value = sc.scalar(15.1, unit='m')
    canvas = Canvas(camera=Camera(**{key: value}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    assert getattr(canvas.camera, key) == value.value


@pytest.mark.parametrize('key', ['near', 'far'])
def test_camera_user_variable_unit_conversion(key):
    value = sc.scalar(33.0, unit='cm')
    canvas = Canvas(camera=Camera(**{key: value}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    canvas._update_camera(limits=_make_limits())
    assert getattr(canvas.camera, key) == 0.33


@pytest.mark.parametrize('key', ['near', 'far'])
def test_camera_user_variable_bad_unit_raises(key):
    value = sc.scalar(6.6, unit='s')
    canvas = Canvas(camera=Camera(**{key: value}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 'm'
    with pytest.raises(sc.UnitError):
        canvas._update_camera(limits=_make_limits())


@pytest.mark.parametrize('key', ['near', 'far'])
def test_camera_user_variable_raises_when_axes_units_are_different(key):
    value = sc.scalar(5.66, unit='m')
    canvas = Canvas(camera=Camera(**{key: value}))
    canvas.xunit = 'm'
    canvas.yunit = 'm'
    canvas.zunit = 's'
    with pytest.raises(sc.UnitError, match='All axes must have the same unit'):
        canvas._update_camera(limits=_make_limits())


def test_toggle_axes_3d():
    canvas = Canvas()
    assert canvas.axes_3d.visible
    canvas.toggle_axes3d()
    assert not canvas.axes_3d.visible
    canvas.toggle_axes3d()
    assert canvas.axes_3d.visible


def test_toggle_outline():
    canvas = Canvas()
    canvas.make_outline(limits=_make_limits())
    assert canvas.outline.visible
    canvas.toggle_outline()
    assert not canvas.outline.visible
    canvas.toggle_outline()
    assert canvas.outline.visible


def test_creation_with_title():
    text = 'My title'
    canvas = Canvas(figsize=(700, 450), title=text)
    assert canvas.title == text
    html = '<i>My</i> <b>title</b>'
    canvas = Canvas(figsize=(700, 450), title=html)
    assert canvas.title == html

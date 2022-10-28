# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import data_array
from plopp.graphics.canvas import Canvas
from plopp.graphics.mesh import Mesh
import scipp as sc


def test_mesh_creation():
    da = data_array(ndim=2)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_binedges():
    da = data_array(ndim=2, binedges=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_masks():
    da = data_array(ndim=2, masks=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_ragged_coord():
    da = data_array(ndim=2, ragged=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert mesh._dim_2d == ('x', 'xx')
    assert mesh._dim_1d == ('y', 'yy')
    assert sc.identical(mesh._data, da)


def test_mesh_update():
    da = data_array(ndim=2)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)
    mesh.update(da * 2.5)
    assert sc.identical(mesh._data, da * 2.5)

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.canvas import Canvas
from plopp.graphics.mesh import Mesh
import scipp as sc


def test_mesh_creation():
    da = dense_data_array(ndim=2)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert mesh._dims == {'x': 'xx', 'y': 'yy'}
    assert sc.identical(mesh._data, da)


def test_mesh_creation_binedges():
    da = dense_data_array(ndim=2, binedges=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_masks():
    da = dense_data_array(ndim=2, masks=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_ragged_coord():
    da = dense_data_array(ndim=2, ragged=True)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert mesh._dims == {'x': 'xx', 'y': 'yy'}
    assert sc.identical(mesh._data, da)


# def test_mesh_get_limits():
#     da = dense_data_array(ndim=2, binedges=True)
#     mesh = Mesh(canvas=Canvas(), data=da)
#     xlims, ylims = mesh.get_limits(xscale='linear', yscale='linear')
#     assert xlims[0] == da.meta['xx'].min()
#     assert xlims[1] == da.meta['xx'].max()
#     assert ylims[0] == da.meta['yy'].min()
#     assert ylims[1] == da.meta['yy'].max()

# def test_mesh_get_limits_log():
#     da = dense_data_array(ndim=2, binedges=True)
#     mesh = Mesh(canvas=Canvas(), data=da)
#     xlims, ylims = mesh.get_limits(xscale='log', yscale='log')
#     assert xlims[0] == da.meta['xx'][1]
#     assert xlims[1] == da.meta['xx'].max()
#     assert ylims[0] == da.meta['yy'][1]
#     assert ylims[1] == da.meta['yy'].max()


def test_mesh_update():
    da = dense_data_array(ndim=2)
    mesh = Mesh(canvas=Canvas(), data=da)
    assert sc.identical(mesh._data, da)
    mesh.update(da * 2.5)
    assert sc.identical(mesh._data, da * 2.5)

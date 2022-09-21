# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.mesh import Mesh
import scipp as sc
from common import make_axes
from dataclasses import dataclass


def test_mesh_creation():
    da = dense_data_array(ndim=2)
    mesh = Mesh(ax=make_axes(), data=da)
    assert mesh._dims == {'x': 'xx', 'y': 'yy'}
    assert sc.identical(mesh._data, da)


def test_mesh_creation_binedges():
    da = dense_data_array(ndim=2, binedges=True)
    mesh = Mesh(ax=make_axes(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_masks():
    da = dense_data_array(ndim=2, masks=True)
    mesh = Mesh(ax=make_axes(), data=da)
    assert sc.identical(mesh._data, da)


def test_mesh_creation_ragged_coord():
    da = dense_data_array(ndim=2, ragged=True)
    mesh = Mesh(ax=make_axes(), data=da)
    assert mesh._dims == {'x': 'xx', 'y': 'yy'}
    assert sc.identical(mesh._data, da)


def test_mesh_get_limits():
    da = dense_data_array(ndim=2, binedges=True)
    mesh = Mesh(ax=make_axes(), data=da)
    xmin, xmax, ymin, ymax = mesh.get_limits(xscale='linear', yscale='linear')
    assert xmin == da.meta['xx'].min()
    assert xmax == da.meta['xx'].max()
    assert ymin == da.meta['yy'].min()
    assert ymax == da.meta['yy'].max()


def test_mesh_get_limits_log():
    da = dense_data_array(ndim=2, binedges=True)
    mesh = Mesh(ax=make_axes(), data=da)
    xmin, xmax, ymin, ymax = mesh.get_limits(xscale='log', yscale='log')
    assert xmin == da.meta['xx'][1]
    assert xmax == da.meta['xx'].max()
    assert ymin == da.meta['yy'][1]
    assert ymax == da.meta['yy'].max()


def test_mesh_get_limits_midpoints():
    da = dense_data_array(ndim=2)
    mesh = Mesh(ax=make_axes(), data=da)
    xmin, xmax, ymin, ymax = mesh.get_limits(xscale='linear', yscale='linear')
    assert xmin < da.meta['xx'].min()
    assert xmax > da.meta['xx'].max()
    assert ymin < da.meta['yy'].min()
    assert ymax > da.meta['yy'].max()


def test_toggle_norm():
    from matplotlib.colors import Normalize, LogNorm
    da = dense_data_array(ndim=2)
    mesh = Mesh(ax=make_axes(), data=da)
    assert mesh._norm_flag == 'linear'
    assert isinstance(mesh._norm_func, Normalize)

    @dataclass
    class Event:
        artist = mesh._cbar.ax

    mesh.toggle_norm(event=Event())
    assert mesh._norm_flag == 'log'
    assert isinstance(mesh._norm_func, LogNorm)


def test_mesh_update():
    da = dense_data_array(ndim=2)
    mesh = Mesh(ax=make_axes(), data=da)
    assert sc.identical(mesh._data, da)
    mesh.update(da * 2.5)
    assert sc.identical(mesh._data, da * 2.5)


def test_mesh_rescale_colormap_on_update():
    da = dense_data_array(ndim=2)
    mesh = Mesh(ax=make_axes(), data=da)
    assert mesh._vmin == da.data.min().value
    assert mesh._vmax == da.data.max().value
    mesh.update(da * 2.5)
    assert mesh._vmin == da.data.min().value * 2.5
    assert mesh._vmax == da.data.max().value * 2.5
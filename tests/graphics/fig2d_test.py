# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import data_array
from plopp.graphics.fig2d import Figure2d
from plopp.graphics.mesh import Mesh
from plopp import input_node
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
import pytest


def test_empty():
    fig = Figure2d()
    assert len(fig.artists) == 0


def test_update():
    fig = Figure2d()
    assert len(fig.artists) == 0
    da = data_array(ndim=2)
    key = 'data2d'
    fig.update(da, key=key)
    assert isinstance(fig.artists[key], Mesh)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_2d_raises():
    fig = Figure2d()
    with pytest.raises(ValueError) as e:
        fig.update(data_array(ndim=1), key='data1d')
    assert str(e.value) == "Figure2d can only be used to plot 2-D data."
    with pytest.raises(ValueError) as e:
        fig.update(data_array(ndim=3), key='data3d')
    assert str(e.value) == "Figure2d can only be used to plot 2-D data."


def test_create_with_node():
    da = data_array(ndim=2)
    fig = Figure2d(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_bin_edges():
    da = data_array(ndim=2, binedges=True)
    fig = Figure2d(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_only_one_bin_edge_coord():
    da = data_array(ndim=2, binedges=True)
    da.coords['xx'] = sc.midpoints(da.coords['xx'])
    fig = Figure2d(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_log_norm():
    fig = Figure2d(norm='log')
    assert fig.colormapper.norm == 'log'


def test_toggle_norm():
    da = data_array(ndim=2)
    fig = Figure2d(input_node(da))
    assert fig.colormapper.norm == 'linear'
    fig.toggle_norm()
    assert fig.colormapper.norm == 'log'


def test_crop():
    da = data_array(ndim=2, binedges=True)
    fig = Figure2d(input_node(da))
    assert fig.canvas.ax.get_xlim() == (da.meta['xx'].min().value,
                                        da.meta['xx'].max().value)
    assert fig.canvas.ax.get_ylim() == (da.meta['yy'].min().value,
                                        da.meta['yy'].max().value)
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    ymin = sc.scalar(5.5, unit='m')
    ymax = sc.scalar(22.3, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax}, yy={'min': ymin, 'max': ymax})
    assert fig.canvas.ax.get_xlim() == (xmin.value, xmax.value)
    assert fig.canvas.ax.get_ylim() == (ymin.value, ymax.value)


def test_crop_no_variable():
    da = data_array(ndim=2)
    xmin = 2.1
    xmax = 102.0
    ymin = 5.5
    ymax = 22.3
    fig = Figure2d(input_node(da),
                   crop={
                       'xx': {
                           'min': xmin,
                           'max': xmax
                       },
                       'yy': {
                           'min': ymin,
                           'max': ymax
                       }
                   })
    assert fig.canvas.ax.get_xlim() == (xmin, xmax)
    assert fig.canvas.ax.get_ylim() == (ymin, ymax)


def test_cbar():
    da = data_array(ndim=2, binedges=True)
    fig = Figure2d(input_node(da), cbar=False)
    assert fig.canvas.cax is None


def test_update_on_one_mesh_changes_colors_on_second_mesh():
    da1 = data_array(ndim=2)
    da2 = 3.0 * data_array(ndim=2)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = input_node(da1)
    b = input_node(da2)
    f = Figure2d(a, b)
    old_b_colors = f.artists[b.id]._mesh.get_facecolors()
    a.func = lambda: da1 * 1.1
    a.notify_children('updated a')
    # No change because the update did not change the colorbar limits
    assert np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    assert not np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())


def test_with_string_coord():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
                      coords={
                          'x': sc.array(dims=['x'], values=strings, unit='s'),
                          'y': sc.arange('y', 5., unit='m')
                      })
    fig = Figure2d(input_node(da))
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
                      coords={
                          'x': sc.array(dims=['x'], values=strings, unit='s'),
                          'y': sc.arange('y', 6., unit='m')
                      })
    fig = Figure2d(input_node(da))
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges_other_coord_is_bin_centers():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
                      coords={
                          'x': sc.array(dims=['x'], values=strings, unit='s'),
                          'y': sc.arange('y', 5., unit='m')
                      })
    fig = Figure2d(input_node(da))
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_kwargs_are_forwarded_to_artist():
    da = data_array(ndim=2)
    fig = Figure2d(input_node(da), rasterized=True)
    artist = list(fig.artists.values())[0]
    assert artist._mesh.get_rasterized()
    fig = Figure2d(input_node(da), rasterized=False)
    artist = list(fig.artists.values())[0]
    assert not artist._mesh.get_rasterized()


def test_figsize():
    da = data_array(ndim=2)
    size = (8.1, 8.3)
    fig = Figure2d(input_node(da), figsize=size)
    assert np.allclose(fig.canvas.fig.get_size_inches(), size)


def test_grid():
    da = data_array(ndim=2)
    fig = Figure2d(input_node(da), grid=True)
    assert fig.canvas.ax.xaxis.get_gridlines()[0].get_visible()


def test_ax():
    fig, ax = plt.subplots()
    assert len(ax.collections) == 0
    da = data_array(ndim=2)
    _ = Figure2d(input_node(da), ax=ax)
    assert len(ax.collections) == 1


def test_cax():
    fig, ax = plt.subplots()
    cax = fig.add_axes([0.9, 0.02, 0.05, 0.98])
    assert len(cax.collections) == 0
    da = data_array(ndim=2)
    _ = Figure2d(input_node(da), ax=ax, cax=cax)
    assert len(cax.collections) > 0

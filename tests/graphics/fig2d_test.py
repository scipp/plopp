# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.fig2d import Figure2d
from plopp.graphics.mesh import Mesh
from plopp import input_node
import numpy as np
import scipp as sc
import pytest


def test_empty():
    fig = Figure2d()
    assert len(fig._children) == 0


def test_update():
    fig = Figure2d()
    assert len(fig._children) == 0
    da = dense_data_array(ndim=2)
    key = 'data2d'
    fig.update(da, key=key)
    assert isinstance(fig._children[key], Mesh)
    assert sc.identical(fig._children[key]._data, da)


def test_update_not_2d_raises():
    fig = Figure2d()
    with pytest.raises(ValueError) as e:
        fig.update(dense_data_array(ndim=1), key='data1d')
    assert str(e.value) == "Figure2d can only be used to plot 2-D data."
    with pytest.raises(ValueError) as e:
        fig.update(dense_data_array(ndim=3), key='data3d')
    assert str(e.value) == "Figure2d can only be used to plot 2-D data."


def test_create_with_node():
    da = dense_data_array(ndim=2)
    fig = Figure2d(input_node(da))
    assert len(fig._children) == 1
    assert sc.identical(list(fig._children.values())[0]._data, da)


def test_log_norm():
    fig = Figure2d(norm='log')
    assert fig.colormapper.norm == 'log'


def test_toggle_norm():
    da = dense_data_array(ndim=2)
    fig = Figure2d(input_node(da))
    assert fig.colormapper.norm == 'linear'
    fig.toggle_norm()
    assert fig.colormapper.norm == 'log'


def test_crop():
    da = dense_data_array(ndim=2, binedges=True)
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


def test_cbar():
    da = dense_data_array(ndim=2, binedges=True)
    fig = Figure2d(input_node(da), cbar=False)
    assert fig.canvas.cax is None


def test_update_on_one_mesh_changes_colors_on_second_mesh():
    da1 = dense_data_array(ndim=2)
    da2 = 3.0 * dense_data_array(ndim=2)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = input_node(da1)
    b = input_node(da2)
    f = Figure2d(a, b)
    old_b_colors = f._children[b.id]._mesh.get_facecolors()
    a.func = lambda: da1 * 1.1
    a.notify_children('updated a')
    # No change because the update did not change the colorbar limits
    assert np.allclose(old_b_colors, f._children[b.id]._mesh.get_facecolors())
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    assert not np.allclose(old_b_colors, f._children[b.id]._mesh.get_facecolors())

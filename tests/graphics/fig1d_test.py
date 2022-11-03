# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import data_array
from plopp.graphics.fig1d import Figure1d
from plopp.graphics.line import Line
from plopp import input_node
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
import pytest


def test_empty():
    fig = Figure1d()
    assert len(fig.artists) == 0


def test_update():
    fig = Figure1d()
    assert len(fig.artists) == 0
    da = data_array(ndim=1)
    key = 'data1d'
    fig.update(da, key=key)
    assert isinstance(fig.artists[key], Line)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_1d_raises():
    fig = Figure1d()
    with pytest.raises(ValueError) as e:
        fig.update(data_array(ndim=2), key='data2d')
    assert str(e.value) == "Figure1d can only be used to plot 1-D data."
    with pytest.raises(ValueError) as e:
        fig.update(data_array(ndim=3), key='data3d')
    assert str(e.value) == "Figure1d can only be used to plot 1-D data."


def test_create_with_node():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    assert line._error is None


def test_with_errorbars():
    da = data_array(ndim=1, variances=True)
    fig = Figure1d(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert line._error is not None
    fig = Figure1d(input_node(da), errorbars=False)
    line = list(fig.artists.values())[0]
    assert line._error is None


def test_with_binedges():
    da = data_array(ndim=1, binedges=True)
    fig = Figure1d(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    xdata = line._line.get_xdata()
    assert np.allclose(xdata, da.coords['xx'].values)
    assert len(xdata) == da.sizes['xx'] + 1


def test_log_norm():
    fig = Figure1d()
    assert fig.canvas.yscale == 'linear'
    fig = Figure1d(norm='log')
    assert fig.canvas.yscale == 'log'


def test_crop():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da))
    assert fig.canvas.ax.get_xlim()[0] < da.meta['xx'].min().value
    assert fig.canvas.ax.get_xlim()[1] > da.meta['xx'].max().value
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax})
    assert fig.canvas.ax.get_xlim() == (xmin.value, xmax.value)
    with pytest.raises(KeyError):
        fig.crop(yy={'min': xmin, 'max': xmax})


def test_crop_no_variable():
    da = data_array(ndim=1)
    xmin = 2.1
    xmax = 33.4
    fig = Figure1d(input_node(da), crop={'xx': {'min': xmin, 'max': xmax}})
    assert fig.canvas.ax.get_xlim() == (xmin, xmax)


def test_update_grows_limits():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da))
    old_lims = fig.canvas.ax.get_ylim()
    key = list(fig.artists.keys())[0]
    fig.update(da * 2.5, key=key)
    new_lims = fig.canvas.ax.get_ylim()
    assert new_lims[0] < old_lims[0]
    assert new_lims[1] > old_lims[1]


def test_update_does_not_shrink_limits():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da))
    old_lims = fig.canvas.ax.get_ylim()
    key = list(fig.artists.keys())[0]
    fig.update(da * 0.5, key=key)
    new_lims = fig.canvas.ax.get_ylim()
    assert new_lims[0] == old_lims[0]
    assert new_lims[1] == old_lims[1]


def test_with_string_coord():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(data=sc.arange('x', 5.),
                      coords={'x': sc.array(dims=['x'], values=strings, unit='m')})
    fig = Figure1d(input_node(da))
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(data=sc.arange('x', 5.),
                      coords={'x': sc.array(dims=['x'], values=strings, unit='m')})
    fig = Figure1d(input_node(da))
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_figsize():
    da = data_array(ndim=1)
    size = (6.1, 3.3)
    fig = Figure1d(input_node(da), figsize=size)
    assert np.allclose(fig.canvas.fig.get_size_inches(), size)


def test_grid():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da), grid=True)
    assert fig.canvas.ax.xaxis.get_gridlines()[0].get_visible()


def test_vmin():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da), vmin=sc.scalar(-0.5, unit='m/s'))
    assert fig.canvas.ax.get_ylim()[0] == -0.5


def test_vmin_unit_mismatch_raises():
    da = data_array(ndim=1)
    with pytest.raises(sc.UnitError):
        _ = Figure1d(input_node(da), vmin=sc.scalar(-0.5, unit='m'))


def test_vmax():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da), vmax=sc.scalar(0.68, unit='m/s'))
    assert fig.canvas.ax.get_ylim()[1] == 0.68


def test_vmin_vmax():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da),
                   vmin=sc.scalar(-0.5, unit='m/s'),
                   vmax=sc.scalar(0.68, unit='m/s'))
    assert np.allclose(fig.canvas.ax.get_ylim(), [-0.5, 0.68])


def test_vmin_vmax_no_variable():
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da), vmin=-0.5, vmax=0.68)
    assert np.allclose(fig.canvas.ax.get_ylim(), [-0.5, 0.68])


def test_ax():
    fig, ax = plt.subplots()
    assert len(ax.lines) == 0
    da = data_array(ndim=1)
    _ = Figure1d(input_node(da), ax=ax)
    assert len(ax.lines) > 0

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data.testing import data_array
from plopp.graphics.fig1d import Figure1d
from plopp.graphics.line import Line
from plopp import input_node
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
import pytest
import tempfile
import os


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
    with pytest.raises(ValueError, match="Figure1d can only be used to plot 1-D data."):
        fig.update(data_array(ndim=2), key='data2d')
    with pytest.raises(ValueError, match="Figure1d can only be used to plot 1-D data."):
        fig.update(data_array(ndim=3), key='data3d')


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


@pytest.mark.parametrize('ext', ['jpg', 'png', 'pdf', 'svg'])
def test_save_to_disk(ext):
    da = data_array(ndim=1)
    fig = Figure1d(input_node(da))
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, f'plopp_fig1d.{ext}')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


def test_raises_for_new_data_with_incompatible_dimension():
    x = data_array(ndim=1)
    y = x.rename(xx='yy')
    with pytest.raises(sc.DimensionError):
        Figure1d(input_node(x), input_node(y))


def test_raises_for_new_data_with_incompatible_unit():
    a = data_array(ndim=1)
    b = a * a
    with pytest.raises(sc.UnitError):
        Figure1d(input_node(a), input_node(b))


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = data_array(ndim=1)
    b = a.copy()
    b.coords['xx'] = a.coords['xx'] * a.coords['xx']
    with pytest.raises(sc.UnitError):
        Figure1d(input_node(a), input_node(b))


def test_converts_new_data_units():
    a = data_array(ndim=1, unit='m')
    b = data_array(ndim=1, unit='cm')
    anode = input_node(a)
    bnode = input_node(b)
    fig = Figure1d(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = data_array(ndim=1)
    b = data_array(ndim=1)
    b.coords['xx'].unit = 'cm'
    anode = input_node(a)
    bnode = input_node(b)
    fig = Figure1d(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['xx'] = c.coords['xx'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)


def test_converts_new_data_units_integers():
    a = sc.DataArray(data=sc.array(dims=['x'], values=[1, 2, 3, 4, 5], unit='m'),
                     coords={'x': sc.arange('x', 5., unit='s')})
    b = sc.DataArray(data=sc.array(dims=['x'], values=[10, 20, 30, 40, 50], unit='cm'),
                     coords={'x': sc.arange('x', 5., unit='s')})
    anode = input_node(a)
    bnode = input_node(b)
    fig = Figure1d(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m', dtype=float))

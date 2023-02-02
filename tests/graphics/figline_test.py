# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp import input_node
from plopp.data.testing import data_array
from plopp.graphics.figline import FigLine


def test_empty():
    fig = FigLine()
    assert len(fig.artists) == 0


def test_update():
    fig = FigLine()
    assert len(fig.artists) == 0
    da = data_array(ndim=1)
    key = 'data1d'
    fig.update(da, key=key)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_1d_raises():
    fig = FigLine()
    with pytest.raises(ValueError, match="FigLine can only be used to plot 1-D data."):
        fig.update(data_array(ndim=2), key='data2d')
    with pytest.raises(ValueError, match="FigLine can only be used to plot 1-D data."):
        fig.update(data_array(ndim=3), key='data3d')


def test_create_with_node():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    assert line._error is None


def test_with_errorbars():
    da = data_array(ndim=1, variances=True)
    fig = FigLine(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert line._error is not None
    fig = FigLine(input_node(da), errorbars=False)
    line = list(fig.artists.values())[0]
    assert line._error is None


def test_with_binedges():
    da = data_array(ndim=1, binedges=True)
    fig = FigLine(input_node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    xdata = line._line.get_xdata()
    assert np.allclose(xdata, da.coords['xx'].values)
    assert len(xdata) == da.sizes['xx'] + 1


def test_log_norm():
    fig = FigLine()
    assert fig.canvas.yscale == 'linear'
    fig = FigLine(norm='log')
    assert fig.canvas.yscale == 'log'


def test_crop():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da))
    assert fig.canvas.xmin < da.meta['xx'].min().value
    assert fig.canvas.xmax > da.meta['xx'].max().value
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax})
    assert fig.canvas.xrange == (xmin.value, xmax.value)
    with pytest.raises(KeyError):
        fig.crop(yy={'min': xmin, 'max': xmax})


def test_crop_no_variable():
    da = data_array(ndim=1)
    xmin = 2.1
    xmax = 33.4
    fig = FigLine(input_node(da), crop={'xx': {'min': xmin, 'max': xmax}})
    assert fig.canvas.xrange == (xmin, xmax)


def test_update_grows_limits():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da))
    old_lims = fig.canvas.yrange
    key = list(fig.artists.keys())[0]
    fig.update(da * 2.5, key=key)
    new_lims = fig.canvas.yrange
    assert new_lims[0] < old_lims[0]
    assert new_lims[1] > old_lims[1]


def test_update_does_not_shrink_limits():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da))
    old_lims = fig.canvas.yrange
    key = list(fig.artists.keys())[0]
    fig.update(da * 0.5, key=key)
    new_lims = fig.canvas.yrange
    assert new_lims[0] == old_lims[0]
    assert new_lims[1] == old_lims[1]


def test_vmin():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da), vmin=sc.scalar(-0.5, unit='m/s'))
    assert fig.canvas.ymin == -0.5


def test_vmin_unit_mismatch_raises():
    da = data_array(ndim=1)
    with pytest.raises(sc.UnitError):
        _ = FigLine(input_node(da), vmin=sc.scalar(-0.5, unit='m'))


def test_vmax():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da), vmax=sc.scalar(0.68, unit='m/s'))
    assert fig.canvas.ymax == 0.68


def test_vmin_vmax():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da),
                  vmin=sc.scalar(-0.5, unit='m/s'),
                  vmax=sc.scalar(0.68, unit='m/s'))
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_vmin_vmax_no_variable():
    da = data_array(ndim=1)
    fig = FigLine(input_node(da), vmin=-0.5, vmax=0.68)
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_raises_for_new_data_with_incompatible_dimension():
    x = data_array(ndim=1)
    y = x.rename(xx='yy')
    with pytest.raises(sc.DimensionError):
        FigLine(input_node(x), input_node(y))


def test_raises_for_new_data_with_incompatible_unit():
    a = data_array(ndim=1)
    b = a * a
    with pytest.raises(sc.UnitError):
        FigLine(input_node(a), input_node(b))


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = data_array(ndim=1)
    b = a.copy()
    b.coords['xx'] = a.coords['xx'] * a.coords['xx']
    with pytest.raises(sc.UnitError):
        FigLine(input_node(a), input_node(b))


def test_converts_new_data_units():
    a = data_array(ndim=1, unit='m')
    b = data_array(ndim=1, unit='cm')
    anode = input_node(a)
    bnode = input_node(b)
    fig = FigLine(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = data_array(ndim=1)
    b = data_array(ndim=1)
    b.coords['xx'].unit = 'cm'
    anode = input_node(a)
    bnode = input_node(b)
    fig = FigLine(anode, bnode)
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
    fig = FigLine(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m', dtype=float))

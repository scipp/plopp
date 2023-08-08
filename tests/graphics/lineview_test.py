# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array
from plopp.graphics.lineview import LineView


def test_empty():
    fig = LineView()
    assert len(fig.artists) == 0


def test_update():
    fig = LineView()
    assert len(fig.artists) == 0
    da = data_array(ndim=1)
    key = 'data1d'
    fig.update(da, key=key)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_1d_raises():
    fig = LineView()
    with pytest.raises(ValueError, match="LineView can only be used to plot 1-D data."):
        fig.update(data_array(ndim=2), key='data2d')
    with pytest.raises(ValueError, match="LineView can only be used to plot 1-D data."):
        fig.update(data_array(ndim=3), key='data3d')


def test_create_with_node():
    da = data_array(ndim=1)
    fig = LineView(Node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    assert line._error is None


def test_with_errorbars():
    da = data_array(ndim=1, variances=True)
    fig = LineView(Node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert line._error is not None
    fig = LineView(Node(da), errorbars=False)
    line = list(fig.artists.values())[0]
    assert line._error is None


def test_with_binedges():
    da = data_array(ndim=1, binedges=True)
    fig = LineView(Node(da))
    assert len(fig.artists) == 1
    line = list(fig.artists.values())[0]
    assert sc.identical(line._data, da)
    xdata = line._line.get_xdata()
    assert np.allclose(xdata, da.coords['xx'].values)
    assert len(xdata) == da.sizes['xx'] + 1


def test_log_norm():
    fig = LineView()
    assert fig.canvas.yscale == 'linear'
    fig = LineView(norm='log')
    assert fig.canvas.yscale == 'log'


def test_update_grows_limits():
    da = data_array(ndim=1)
    fig = LineView(Node(da))
    old_lims = fig.canvas.yrange
    key = list(fig.artists.keys())[0]
    fig.update(da * 2.5, key=key)
    new_lims = fig.canvas.yrange
    assert new_lims[0] < old_lims[0]
    assert new_lims[1] > old_lims[1]


def test_update_does_shrink_limits_if_auto_mode():
    da = data_array(ndim=1)
    fig = LineView(Node(da), autoscale='auto')
    old_lims = fig.canvas.yrange
    key = list(fig.artists.keys())[0]
    const = 0.5
    fig.update(da * const, key=key)
    new_lims = fig.canvas.yrange
    assert new_lims[0] == old_lims[0] * const
    assert new_lims[1] == old_lims[1] * const


def test_update_does_not_shrink_limits_if_grow_mode():
    da = data_array(ndim=1)
    fig = LineView(Node(da), autoscale='grow')
    old_lims = fig.canvas.yrange
    key = list(fig.artists.keys())[0]
    fig.update(da * 0.5, key=key)
    new_lims = fig.canvas.yrange
    assert new_lims[0] == old_lims[0]
    assert new_lims[1] == old_lims[1]


def test_vmin():
    da = data_array(ndim=1)
    fig = LineView(Node(da), vmin=sc.scalar(-0.5, unit='m/s'))
    assert fig.canvas.ymin == -0.5


def test_vmin_unit_mismatch_raises():
    da = data_array(ndim=1)
    with pytest.raises(sc.UnitError):
        _ = LineView(Node(da), vmin=sc.scalar(-0.5, unit='m'))


def test_vmax():
    da = data_array(ndim=1)
    fig = LineView(Node(da), vmax=sc.scalar(0.68, unit='m/s'))
    assert fig.canvas.ymax == 0.68


def test_vmin_vmax():
    da = data_array(ndim=1)
    fig = LineView(
        Node(da),
        vmin=sc.scalar(-0.5, unit='m/s'),
        vmax=sc.scalar(0.68, unit='m/s'),
    )
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_vmin_vmax_no_variable():
    da = data_array(ndim=1)
    fig = LineView(Node(da), vmin=-0.5, vmax=0.68)
    assert np.allclose(fig.canvas.yrange, [-0.5, 0.68])


def test_raises_for_new_data_with_incompatible_dimension():
    x = data_array(ndim=1)
    y = x.rename(xx='yy')
    with pytest.raises(sc.DimensionError):
        LineView(Node(x), Node(y))


def test_raises_for_new_data_with_incompatible_unit():
    a = data_array(ndim=1)
    b = a * a
    with pytest.raises(sc.UnitError):
        LineView(Node(a), Node(b))


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = data_array(ndim=1)
    b = a.copy()
    b.coords['xx'] = a.coords['xx'] * a.coords['xx']
    with pytest.raises(sc.UnitError):
        LineView(Node(a), Node(b))


def test_converts_new_data_units():
    a = data_array(ndim=1, unit='m')
    b = data_array(ndim=1, unit='cm')
    anode = Node(a)
    bnode = Node(b)
    fig = LineView(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = data_array(ndim=1)
    b = data_array(ndim=1)
    b.coords['xx'].unit = 'cm'
    anode = Node(a)
    bnode = Node(b)
    fig = LineView(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['xx'] = c.coords['xx'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)


def test_converts_new_data_units_integers():
    a = sc.DataArray(
        data=sc.array(dims=['x'], values=[1, 2, 3, 4, 5], unit='m'),
        coords={'x': sc.arange('x', 5.0, unit='s')},
    )
    b = sc.DataArray(
        data=sc.array(dims=['x'], values=[10, 20, 30, 40, 50], unit='cm'),
        coords={'x': sc.arange('x', 5.0, unit='s')},
    )
    anode = Node(a)
    bnode = Node(b)
    fig = LineView(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m', dtype=float))

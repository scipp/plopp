# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

import plopp as pp


def test_xyplot_variable():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('x', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y)
    assert fig.canvas.xlabel == 'time [s]'
    assert fig.canvas.ylabel == '[K]'


def test_xyplot_ndarray():
    N = 50
    x = sc.arange('distance', float(N), unit='m')
    y = sc.linspace('speed', -44.0, 44.0, N, unit='m/s')
    pp.xyplot(x.values, y)
    pp.xyplot(x, y.values)


def test_xyplot_list():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('x', 100.0, 120.0, unit='K')
    pp.xyplot(x.values.tolist(), y)
    pp.xyplot(x, y.values.tolist())


def test_xyplot_data_array_raises():
    x = sc.arange('time', 20.0, unit='s')
    y = pp.data.data1d()
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.xyplot(x, y)
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.xyplot(y, x)


def test_xyplot_2d_variable_raises():
    x = pp.data.data2d().data
    y = sc.arange('time', 20.0, unit='s')
    with pytest.raises(sc.DimensionError, match='Expected 1 dimensions, got 2'):
        pp.xyplot(x, y)
    with pytest.raises(sc.DimensionError, match='Expected 1 dimensions, got 2'):
        pp.xyplot(y, x)


def test_xyplot_variable_kwargs():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('x', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y, color='red', vmin=102.0, vmax=115.0)
    assert np.allclose(fig.canvas.yrange, [102.0, 115.0])
    line = list(fig.artists.values())[0]
    assert line.color == 'red'


def test_xyplot_bin_edges():
    x = sc.arange('time', 21.0, unit='s')
    y = sc.arange('x', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y)
    line = list(fig.artists.values())[0]
    assert len(line._line.get_xdata()) == 21

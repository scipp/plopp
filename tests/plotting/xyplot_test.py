# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

import plopp as pp

pytestmark = pytest.mark.usefixtures("_parametrize_all_backends")


def test_xyplot_variable():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('time', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y)
    assert fig.canvas.xlabel == 'time [s]'
    assert fig.canvas.ylabel == '[K]'


def test_xyplot_ndarray():
    N = 50
    x = np.arange(float(N))
    y = np.linspace(-44.0, 44.0, N)
    pp.xyplot(x, y)


def test_xyplot_list():
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 0, 1]
    pp.xyplot(x, y)


def test_xyplot_different_dims_raises():
    x = sc.arange('x', 20.0, unit='s')
    y = sc.arange('y', 100.0, 120.0, unit='K')
    with pytest.raises(sc.DimensionError, match='Dimensions of x and y must match'):
        pp.xyplot(x, y)


def test_xyplot_data_array_raises():
    x = sc.arange('x', 20.0, unit='s')
    y = pp.data.data1d()
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.xyplot(x, y)
    with pytest.raises(TypeError, match='Cannot convert input of type'):
        pp.xyplot(y, x)


def test_xyplot_2d_variable_raises():
    x = sc.arange('x', 50.0, unit='s')
    y = pp.data.data2d().data
    with pytest.raises(sc.DimensionError, match='Expected 1 dimensions, got 2'):
        pp.xyplot(x, y)
    with pytest.raises(sc.DimensionError, match='Expected 1 dimensions, got 2'):
        pp.xyplot(y, x)


def test_xyplot_variable_kwargs():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('time', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y, color='red', vmin=102.0, vmax=115.0)
    assert np.allclose(fig.canvas.yrange, [102.0, 115.0])
    [line] = fig.artists.values()
    assert line.color == 'red'


def test_xyplot_bin_edges():
    x = sc.arange('time', 21.0, unit='s')
    y = sc.arange('time', 100.0, 120.0, unit='K')
    fig = pp.xyplot(x, y)
    [line] = fig.artists.values()
    ldata = line._data
    assert len(ldata.coords[ldata.dim]) == len(ldata.data) + 1


def test_xyplot_from_nodes():
    x = sc.arange('time', 20.0, unit='s')
    y = sc.arange('time', 100.0, 120.0, unit='K')
    pp.xyplot(pp.Node(x), y)
    pp.xyplot(x, pp.Node(y))
    pp.xyplot(pp.Node(x), pp.Node(y))

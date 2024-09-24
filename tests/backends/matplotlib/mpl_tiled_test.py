# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest

from plopp.backends.matplotlib.tiled import Tiled
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_copy():
    da = data_array(ndim=1)
    original = da.plot()
    copy = original.copy()
    assert original.graph_nodes.keys() == copy.graph_nodes.keys()
    assert original.artists.keys() == copy.artists.keys()


def test_copy_keeps_kwargs():
    da = data_array(ndim=1)
    original = da.plot(
        scale={'xx': 'log'},
        norm='log',
        grid=True,
        title='A nice title',
    )
    copy = original.copy()
    assert copy.canvas.xscale == 'log'
    assert copy.canvas.yscale == 'log'
    assert copy.canvas.grid
    assert copy.canvas.title == 'A nice title'


def test_side_by_side():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=1, ncols=2)
    tiled[0, 0] = da1.plot()
    tiled[0, 1] = da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 2


def test_top_bottom():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=2, ncols=1)
    tiled[0, 0] = da1.plot()
    tiled[1, 0] = da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 1


def test_grid():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=2, ncols=2)
    tiled[0, 0] = da1.plot()
    tiled[0, 1] = da2.plot()
    tiled[1, 0] = da1.plot()
    tiled[1, 1] = da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_range():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = Tiled(nrows=1, ncols=3)
    tiled[0, :2] = da1.plot()
    tiled[0, 2] = da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_add():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled2 = Tiled(nrows=1, ncols=2)
    tiled2[0, 0] = da3.plot()
    tiled2[0, 1] = da4.plot()
    tiled = tiled1 + tiled2
    assert tiled.nrows == 1
    assert tiled.ncols == 4


def test_add_tiled_figure():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled = tiled1 + da3.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_add_figure_tiled():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled = da3.plot() + tiled1
    assert tiled.nrows == 1
    assert tiled.ncols == 3


def test_divide():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=2)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled2 = Tiled(nrows=1, ncols=2)
    tiled2[0, 0] = da3.plot()
    tiled2[0, 1] = da4.plot()
    tiled = tiled1 / tiled2
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_divide_tiled_figure():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=3)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled1[0, 2] = da3.plot()
    tiled = tiled1 / da4.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 3


def test_divide_figure_tiled():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled1 = Tiled(nrows=1, ncols=3)
    tiled1[0, 0] = da1.plot()
    tiled1[0, 1] = da2.plot()
    tiled1[0, 2] = da3.plot()
    tiled = da4.plot() / tiled1
    assert tiled.nrows == 2
    assert tiled.ncols == 3


def test_figure_add():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = da1.plot() + da2.plot()
    assert tiled.nrows == 1
    assert tiled.ncols == 2


def test_figure_divide():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    tiled = da1.plot() / da2.plot()
    assert tiled.nrows == 2
    assert tiled.ncols == 1


def test_figure_operators():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=2)
    da3 = data_array(ndim=1, binedges=True)
    da4 = data_array(ndim=2, binedges=True)
    tiled = (da1.plot() + da2.plot()) / (da3.plot() + da4.plot())
    assert tiled.nrows == 2
    assert tiled.ncols == 2


def test_tiled_keeps_figure_kwargs():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=1) * 3.3
    p1 = da1.plot(grid=True, title="My Title", vmin=-2.3, vmax=10)
    p2 = da2.plot(norm='log')
    tiled = p1 + p2
    assert tiled[0, 0].canvas.grid
    assert tiled[0, 0].canvas.title == "My Title"
    assert tiled[0, 0].canvas.ymin == -2.3
    assert tiled[0, 0].canvas.ymax == 10
    assert tiled[0, 1].canvas.yscale == 'log'


def test_tiled_keeps_figure_props():
    da1 = data_array(ndim=1)
    da2 = data_array(ndim=1) * 3.3
    p1 = da1.plot()
    p2 = da2.plot()
    p1.canvas.logy()
    p2.canvas.logx()
    tiled = p1 + p2
    assert tiled[0, 0].canvas.xscale == 'linear'
    assert tiled[0, 0].canvas.yscale == 'log'
    assert tiled[0, 1].canvas.xscale == 'log'
    assert tiled[0, 1].canvas.yscale == 'linear'


def test_tiled_keeps_aspect():
    a = data_array(ndim=2)
    f1 = a.plot(aspect='equal')
    f2 = a.plot(cbar=False)
    tiled = f1 + f2
    assert tiled.fig.get_axes()[0].get_aspect() == 1.0
    assert tiled.fig.get_axes()[2].get_aspect() == "auto"

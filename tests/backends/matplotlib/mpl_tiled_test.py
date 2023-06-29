# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


from plopp.backends.matplotlib.tiled import Tiled
from plopp.data.testing import data_array


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

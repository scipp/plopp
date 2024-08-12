# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array

pp.backends['2d'] = 'matplotlib'


def test_figsize():
    da = data_array(ndim=1)
    size = (8.1, 8.3)
    fig = da.plot(figsize=size)
    assert np.allclose(fig.canvas.fig.get_size_inches(), size)


def test_grid():
    da = data_array(ndim=1)
    fig = da.plot(grid=True)
    assert fig.canvas.ax.xaxis.get_gridlines()[0].get_visible()


def test_ax():
    _, ax = plt.subplots()
    assert len(ax.collections) == 0
    da = data_array(ndim=2)
    _ = da.plot(ax=ax)
    assert len(ax.collections) == 1


def test_cax():
    fig, ax = plt.subplots()
    cax = fig.add_axes([0.9, 0.02, 0.05, 0.98])
    assert len(cax.collections) == 0
    da = data_array(ndim=2)
    _ = da.plot(ax=ax, cax=cax)
    assert len(cax.collections) > 0


def test_hide_legend():
    da1 = data_array(ndim=1)
    da2 = da1 * 3.3
    p = pp.plot({'a': da1, 'b': da2}, legend=False)
    leg = p.ax.get_legend()
    assert leg is None


def test_legend_location():
    da1 = data_array(ndim=1)
    da2 = da1 * 3.3
    data = {'a': da1, 'b': da2}
    leg1 = pp.plot(data, legend=(0.5, 0.5)).ax.get_legend().get_window_extent().bounds
    leg2 = pp.plot(data, legend=(0.9, 0.5)).ax.get_legend().get_window_extent().bounds
    leg3 = pp.plot(data, legend=(0.5, 0.9)).ax.get_legend().get_window_extent().bounds
    assert leg2[0] > leg1[0]
    assert leg2[1] == leg1[1]
    assert leg3[1] > leg1[1]
    assert leg3[0] == leg1[0]

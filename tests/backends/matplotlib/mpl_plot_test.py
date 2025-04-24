# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


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
    assert len(ax.lines) == 0
    assert len(ax.collections) == 0
    assert len(ax.images) == 0
    data_array(ndim=1).plot(ax=ax)
    assert len(ax.lines) > 0
    data_array(ndim=2, linspace=False).plot(ax=ax)
    assert len(ax.collections) == 1
    data_array(ndim=2, linspace=True).plot(ax=ax)
    assert len(ax.images) == 1


def test_cax():
    fig, ax = plt.subplots()
    cax = fig.add_axes([0.9, 0.02, 0.05, 0.98])
    assert len(ax.collections) == 0
    da = data_array(ndim=2, linspace=False)
    fig = da.plot(ax=ax, cax=cax)
    assert len(ax.collections) > 0
    assert fig.canvas.cax is cax


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


def test_no_legend_for_single_artist():
    da = data_array(ndim=1)
    da.name = "Velocity"
    p = pp.plot(da)
    leg = p.ax.get_legend()
    assert leg is None


def test_legend_is_removed_when_only_one_artist_is_left():
    a = data_array(ndim=1)
    b = 2.3 * a
    f = pp.plot({'a': a, 'b': b})
    ka, _ = f.view.artists.keys()
    f.view.remove(ka)
    assert f.ax.get_legend() is None


def test_legend_entry_is_removed_when_artist_is_removed():
    a = data_array(ndim=1)
    b = 2.3 * a
    c = 0.8 * a
    f = pp.plot({'a': a, 'b': b, 'c': c})
    ka, _, _ = f.view.artists.keys()
    f.view.remove(ka)
    texts = f.ax.get_legend().get_texts()
    assert len(texts) == 2
    assert texts[0].get_text() == 'b'
    assert texts[1].get_text() == 'c'


def test_with_string_coord_1d():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(
        data=sc.arange('x', 5.0),
        coords={'x': sc.array(dims=['x'], values=strings, unit='m')},
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges_1d():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(
        data=sc.arange('x', 5.0),
        coords={'x': sc.array(dims=['x'], values=strings, unit='m')},
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_string_coord_2d():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 5.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges_2d():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 6.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges_other_coord_is_bin_centers_2d():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 5.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_polar_axes_limits_with_padding_are_clipped():
    # Make some spiral data
    N = 50
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 0.995 * 2 * np.pi, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})

    _, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    fig = pp.plot(da, ax=ax)
    assert fig.canvas.xrange == (0, 2 * np.pi)


def test_polar_axes_limits_more_than_two_pi_are_clipped():
    # Make some spiral data
    N = 50
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 3.5 * 2 * np.pi, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})

    _, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    fig = pp.plot(da, ax=ax)
    assert fig.canvas.xrange == (0, 2 * np.pi)


def test_polar_axes_limits_small_range_fits_to_data():
    # Make some spiral data
    N = 50
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0.25 * 2 * np.pi, 0.75 * 2 * np.pi, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})

    _, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    fig = pp.plot(da, ax=ax)
    assert fig.canvas.xmin > 0.0
    assert fig.canvas.xmax < 2 * np.pi


def test_aspect_ratio():
    da = data_array(ndim=1)
    fig = da.plot(aspect='equal')
    assert fig.canvas.ax.get_aspect() == 1.0
    da = data_array(ndim=2)
    fig = da.plot(aspect='equal')
    assert fig.canvas.ax.get_aspect() == 1.0

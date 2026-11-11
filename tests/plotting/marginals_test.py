# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_marginals_creates_all_axes():
    da = data_array(ndim=2)
    fig = pp.marginals(da)
    main, _, _, cax = fig.canvas.fig.axes
    assert fig.canvas.ax is main
    assert fig.canvas.cax is cax


def test_marginals_from_node():
    da = data_array(ndim=2)
    pp.marginals(pp.Node(da))


def test_marginals_marginal_values():
    da = data_array(ndim=2)
    fig = pp.marginals(da)
    _, top, side, _ = fig.canvas.fig.axes
    top_line = top.lines[0]
    side_line = side.lines[0]
    xdim, ydim = da.dims[1], da.dims[0]
    np.testing.assert_allclose(top_line.get_xdata(), da.coords[xdim].values)
    np.testing.assert_allclose(top_line.get_ydata(), da.sum(ydim).values)
    np.testing.assert_allclose(side_line.get_xdata(), da.sum(xdim).values)
    np.testing.assert_allclose(side_line.get_ydata(), da.coords[ydim].values)


def test_marginals_updates_when_node_changes():
    da = data_array(ndim=2)
    node = pp.Node(da)
    fig = pp.marginals(node)
    _, top, side, _ = fig.canvas.fig.axes
    node.func = lambda: da * 2.0
    node.notify_children('updated')
    np.testing.assert_allclose(
        top.lines[0].get_ydata(), (da * 2.0).sum(da.dims[0]).values
    )
    np.testing.assert_allclose(
        side.lines[0].get_xdata(), (da * 2.0).sum(da.dims[1]).values
    )


def test_marginals_side_left():
    da = data_array(ndim=2)
    fig = pp.marginals(da, side='left')
    main, top, side, _ = fig.canvas.fig.axes
    assert side.xaxis_inverted()
    assert not main.xaxis_inverted()
    assert main.get_ylabel() == ''
    assert side.get_ylabel() == f'{da.dims[0]} [m]'
    assert side.get_xlabel() == top.get_ylabel()
    assert top.get_xlabel() == ''
    assert main.get_xlabel() == f'{da.dims[1]} [m]'


def test_marginals_side_right():
    da = data_array(ndim=2)
    fig = pp.marginals(da, side='right')
    main, top, side, _ = fig.canvas.fig.axes
    assert not side.xaxis_inverted()
    assert main.get_ylabel() == f'{da.dims[0]} [m]'
    assert side.get_ylabel() == ''
    assert side.get_xlabel() == top.get_ylabel()
    assert top.get_xlabel() == ''


def test_marginals_side_axes_position():
    da = data_array(ndim=2)
    fig_left = pp.marginals(da, side='left')
    fig_right = pp.marginals(da, side='right')
    fig_left.canvas.fig.draw_without_rendering()
    fig_right.canvas.fig.draw_without_rendering()
    main_l, _, side_l, _ = fig_left.canvas.fig.axes
    main_r, _, side_r, _ = fig_right.canvas.fig.axes
    assert side_l.get_position().x1 <= main_l.get_position().x0
    assert side_r.get_position().x0 >= main_r.get_position().x1


def test_marginals_title():
    da = data_array(ndim=2)
    fig = pp.marginals(da, title='My title')
    _, top, _, _ = fig.canvas.fig.axes
    assert top.get_title() == 'My title'


def test_marginals_with_existing_ax():
    da = data_array(ndim=2)
    f, ax = plt.subplots()
    fig = pp.marginals(da, ax=ax)
    assert fig.canvas.ax is ax
    assert len(f.axes) == 4


def test_marginals_forwards_kwargs():
    da = data_array(ndim=2)
    fig = pp.marginals(da, grid=True)
    main, top, side, _ = fig.canvas.fig.axes
    for ax in (main, top, side):
        assert ax.xaxis.get_gridlines()[0].get_visible()


def test_marginals_small_known_values():
    da = sc.DataArray(
        data=sc.array(dims=['a', 'b'], values=np.arange(12.0).reshape(3, 4), unit='K'),
        coords={
            'a': sc.arange('a', 3.0, unit='s'),
            'b': sc.arange('b', 4.0, unit='m'),
        },
    )
    fig = pp.marginals(da)
    _, top, side, _ = fig.canvas.fig.axes
    np.testing.assert_allclose(top.lines[0].get_ydata(), [12.0, 15.0, 18.0, 21.0])
    np.testing.assert_allclose(side.lines[0].get_xdata(), [6.0, 22.0, 38.0])

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import numpy as np
import pytest
import scipp as sc

from plopp.backends.matplotlib import MatplotlibBackend
from plopp.backends.matplotlib.interactive import InteractiveFig
from plopp.backends.matplotlib.static import StaticFig
from plopp.core import Node
from plopp.graphics.imageview import ImageView
from plopp.graphics.lineview import LineView


def test_create_static_fig1d():
    b = MatplotlibBackend()
    fig = b.figure1d(View=LineView)
    assert isinstance(fig, StaticFig)


@pytest.mark.usefixtures("_use_ipympl")
def test_create_interactive_fig1d():
    b = MatplotlibBackend()
    fig = b.figure1d(View=LineView)
    assert isinstance(fig, InteractiveFig)


def test_create_static_fig2d():
    b = MatplotlibBackend()
    fig = b.figure2d(View=ImageView)
    assert isinstance(fig, StaticFig)


@pytest.mark.usefixtures("_use_ipympl")
def test_create_interactive_fig2d():
    b = MatplotlibBackend()
    fig = b.figure2d(View=ImageView)
    assert isinstance(fig, InteractiveFig)


def test_datetime_compatibility_between_1d_and_2d_figures():
    b = MatplotlibBackend()
    # 2d data
    t = np.arange(
        np.datetime64('2017-03-16T20:58:17'), np.datetime64('2017-03-16T21:15:17'), 20
    )
    time = sc.array(dims=['time'], values=t)
    z = sc.arange('z', 50.0, unit='m')
    v = 10 * np.random.random(z.shape + time.shape)
    da2d = sc.DataArray(
        data=sc.array(dims=['z', 'time'], values=v), coords={'time': time, 'z': z}
    )
    fig = b.figure2d(ImageView, Node(da2d))
    assert len(fig.ax.lines) == 0
    assert len(fig.ax.collections) == 1

    # 1d data
    v = np.random.rand(time.sizes['time'])
    da1d = sc.DataArray(data=sc.array(dims=['time'], values=v), coords={'time': time})
    b.figure1d(LineView, Node(da1d), ax=fig.ax)
    assert len(fig.ax.lines) > 0
    assert len(fig.ax.collections) == 1

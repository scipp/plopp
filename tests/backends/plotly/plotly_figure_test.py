# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.backends.plotly.figure import Figure
from plopp.data.testing import data_array
from plopp.graphics.lineview import LineView
from plopp.graphics.polarview import PolarLineView

pytest.importorskip("plotly")


def test_creation():
    da = data_array(ndim=1)
    fig = Figure(LineView, pp.Node(da))
    assert fig.canvas.xlabel == f'xx [{da.coords["xx"].unit}]'
    assert fig.canvas.ylabel == f'[{da.unit}]'


def test_logx_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Figure(LineView, pp.Node(da), scale={'xx': 'log'})
    assert fig.toolbar['logx'].value


def test_logy_1d_toolbar_button():
    da = data_array(ndim=1)
    fig = Figure(LineView, pp.Node(da), norm='log')
    assert fig.toolbar['logy'].value


def test_polar_figure():
    N = 150
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 12, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})
    f = Figure(PolarLineView, pp.Node(da))
    assert np.array_equal(f.canvas.xrange, (0, 2 * np.pi))


def test_polar_figure_set_xrange():
    N = 150
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 12, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})
    f = Figure(PolarLineView, pp.Node(da))
    f.canvas.xrange = (0.5, 11.0)
    assert np.array_equal(f.canvas.xrange, (0.5, 11.0))


def test_polar_figure_set_yrange():
    N = 150
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 12, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})
    f = Figure(PolarLineView, pp.Node(da))
    f.canvas.yrange = (0.5, 8.0)
    assert np.array_equal(f.canvas.yrange, (0.5, 8.0))

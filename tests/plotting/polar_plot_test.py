# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array, dataset


def test_polar_plot_1d_wrap_around_2_pi():
    N = 150
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 12, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})
    f = pp.polar(da)
    assert f.canvas.xrange == (0, 2 * np.pi)


def test_polar_plot_1d_small_range():
    N = 150
    r = sc.linspace('theta', 0, 10, N, unit='m')
    theta = sc.linspace('theta', 0, 4, N, unit='rad')
    da = sc.DataArray(data=r, coords={'theta': theta})
    f = pp.polar(da)
    assert f.canvas.xmin < 0
    assert f.canvas.xmax < 2 * np.pi


def test_polar_plot_2d_2_pi():
    da = data_array(ndim=2, binedges=True, unit='K')
    xdim = da.dims[-1]
    da.coords[xdim] = sc.linspace(xdim, 0, 2 * np.pi, da.sizes[xdim] + 1, unit='rad')
    f = pp.polar(da)
    assert f.canvas.xrange == (0, 2 * np.pi)


def test_polar_plot_2d_small_range():
    da = data_array(ndim=2, binedges=True, unit='K')
    xdim = da.dims[-1]
    da.coords[xdim] = sc.linspace(xdim, 0, 1.3 * np.pi, da.sizes[xdim] + 1, unit='rad')
    f = pp.polar(da)
    assert f.canvas.xrange == (0, 1.3 * np.pi)

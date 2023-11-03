# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest

import plopp as pp
from plopp.backends.matplotlib.residuals import residuals
from plopp.data.testing import data_array


def test_single_line():
    ref = data_array(ndim=1)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    fig1 = ref.plot()
    fig2 = a.plot()
    fig = residuals(fig2, fig1)
    assert len(fig.main_panel.fig.get_axes()) == 2
    assert len(fig.main_panel.artists) == 2
    assert len(fig.res_panel.artists) == 1


def test_three_lines():
    ref = data_array(ndim=1)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    b = ref.copy()
    b.values += np.random.uniform(-1.0, 1.0, size=len(b))
    c = ref.copy()
    fig1 = ref.plot()
    fig2 = pp.plot({'a': a, 'b': b, 'c': c})
    fig = residuals(fig2, fig1)
    assert len(fig.main_panel.artists) == 4
    assert len(fig.res_panel.artists) == 3


def test_with_bin_edges():
    ref = data_array(ndim=1, binedges=True)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    fig1 = ref.plot()
    fig2 = a.plot()
    fig = residuals(fig2, fig1)
    for artist in fig.main_panel.artists.values():
        assert artist._line.get_linestyle() == '-'
    for artist in fig.res_panel.artists.values():
        assert artist._line.get_linestyle() == '-'


def test_raises_when_given_2d_plots():
    da1d = data_array(ndim=1)
    da2d = data_array(ndim=2)
    msg = "The residual plot only supports 1d figures."
    with pytest.raises(TypeError, match=msg):
        residuals(da2d.plot(), da1d.plot())
    with pytest.raises(TypeError, match=msg):
        residuals(da1d.plot(), da2d.plot())
    with pytest.raises(TypeError, match=msg):
        residuals(da2d.plot(), da2d.plot())


def test_raises_when_reference_contains_multiple_lines():
    ref = data_array(ndim=1)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    b = ref.copy()
    b.values += np.random.uniform(-1.0, 1.0, size=len(b))
    fig1 = pp.plot({'a': a, 'b': b})
    fig2 = ref.plot()
    with pytest.raises(
        TypeError,
        match="The reference figure must contain exactly one line",
    ):
        residuals(fig2, fig1)


def test_single_line_operator_minus():
    ref = data_array(ndim=1)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    fig1 = ref.plot()
    fig2 = a.plot()
    fig = fig2 - fig1
    assert len(fig.main_panel.fig.get_axes()) == 2
    assert len(fig.main_panel.artists) == 2
    assert len(fig.res_panel.artists) == 1


def test_three_lines_operator_minus():
    ref = data_array(ndim=1)
    a = ref.copy()
    a.values += np.random.uniform(-0.25, 0.25, size=len(a))
    b = ref.copy()
    b.values += np.random.uniform(-1.0, 1.0, size=len(b))
    c = ref.copy()
    fig1 = ref.plot()
    fig2 = pp.plot({'a': a, 'b': b, 'c': c})
    fig = fig2 - fig1
    assert len(fig.main_panel.artists) == 4
    assert len(fig.res_panel.artists) == 3

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.backends.matplotlib.canvas import Canvas
from plopp.backends.matplotlib.scatter import Scatter
from plopp.data.testing import scatter as scatter_data

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_scatter_creation():
    da = scatter_data()
    scat = Scatter(canvas=Canvas(), data=da)
    assert scat._unit == da.unit
    assert len(scat._scatter.get_offsets()) == len(da)
    x, y = scat._scatter.get_offsets().T
    assert np.allclose(x, da.coords['x'].values)
    assert np.allclose(y, da.coords['y'].values)
    assert not scat._mask.get_visible()


def test_scatter_with_mask():
    da = scatter_data()
    da.masks['mask'] = da.coords['x'] > sc.scalar(5, unit='m')
    scat = Scatter(canvas=Canvas(), data=da)
    assert scat._mask.get_visible()
    expected = da[da.masks['mask']]
    x, y = scat._mask.get_offsets().T
    assert np.allclose(x[~np.isnan(x)], expected.coords['x'].values)
    assert np.allclose(y[~np.isnan(y)], expected.coords['y'].values)


def test_scatter_update():
    da = scatter_data()
    scat = Scatter(canvas=Canvas(), data=da)
    x, y = scat._scatter.get_offsets().T
    assert np.allclose(x, da.coords['x'].values)
    assert np.allclose(y, da.coords['y'].values)
    new = da.copy()
    new.coords['x'] += sc.scalar(1.1, unit=da.coords['x'].unit)
    new.coords['y'] *= 2.3
    scat.update(new)
    x, y = scat._scatter.get_offsets().T
    assert np.allclose(x, new.coords['x'].values)
    assert np.allclose(y, new.coords['y'].values)


def test_scatter_no_legend_for_a_single_artist():
    da = scatter_data()
    da.name = "SomeScatterData"
    fig = pp.scatter(da)
    leg = fig.ax.get_legend()
    assert leg is None


def test_scatter_has_legend_for_multiple_artists():
    a = scatter_data(seed=1)
    b = scatter_data(seed=2)
    fig = pp.scatter({'a': a, 'b': b})
    leg = fig.ax.get_legend()
    assert leg is not None
    texts = leg.get_texts()
    assert len(texts) == 2
    assert texts[0].get_text() == 'a'
    assert texts[1].get_text() == 'b'

    c = scatter_data(seed=3)
    fig = pp.scatter({'a': a, 'b': b, 'c': c})
    leg = fig.ax.get_legend()
    assert leg is not None
    texts = leg.get_texts()
    assert len(texts) == 3
    assert texts[0].get_text() == 'a'
    assert texts[1].get_text() == 'b'
    assert texts[2].get_text() == 'c'

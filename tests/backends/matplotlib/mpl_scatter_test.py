# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import scipp as sc

from plopp.backends.matplotlib.canvas import Canvas
from plopp.backends.matplotlib.scatter import Scatter
from plopp.data.testing import scatter as scatter_data


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

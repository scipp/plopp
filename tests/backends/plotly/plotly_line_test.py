# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.backends.plotly.canvas import Canvas
from plopp.backends.plotly.line import Line
from plopp.data.testing import data_array

pytest.importorskip("plotly")


def test_line_creation():
    da = data_array(ndim=1, unit='K')
    line = Line(canvas=Canvas(), data=da)
    assert line._unit == 'K'
    assert line._dim == 'xx'
    assert len(line._line.x) == da.sizes['xx']
    assert np.allclose(line._line.x, da.meta['xx'].values)
    assert np.allclose(line._line.y, da.values)
    assert line._error is None
    assert not line._mask.visible


def test_line_creation_bin_edges():
    da = data_array(ndim=1, binedges=True)
    line = Line(canvas=Canvas(), data=da)
    assert len(line._line.x) == da.sizes['xx'] + 1


def test_line_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._error.error_y['array'], sc.stddevs(da.data).values)


def test_line_hide_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da, errorbars=False)
    assert line._error is None


def test_line_with_mask():
    da = data_array(ndim=1, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.visible


def test_line_update():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._line.x, da.meta['xx'].values)
    assert np.allclose(line._line.y, da.values)
    line.update(da * 2.5)
    assert np.allclose(line._line.x, da.meta['xx'].values)
    assert np.allclose(line._line.y, da.values * 2.5)


def test_line_update_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._line.y, da.values)
    assert np.allclose(line._error.error_y['array'], sc.stddevs(da.data).values)
    new_values = da * 3.3
    new_values.variances = da.variances
    line.update(new_values)
    assert np.allclose(line._line.y, da.values * 3.3)
    assert np.allclose(line._error.error_y['array'], sc.stddevs(da.data).values)
    new_values = 1.0 * da
    new_values.variances = da.variances * 4.0
    line.update(new_values)
    assert np.allclose(line._line.y, da.values)
    assert np.allclose(line._error.error_y['array'], sc.stddevs(da.data).values * 2.0)

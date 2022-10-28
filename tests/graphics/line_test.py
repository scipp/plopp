# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import data_array
from plopp.graphics.canvas import Canvas
from plopp.graphics.line import Line
import numpy as np
import scipp as sc


def test_line_creation():
    da = data_array(ndim=1, unit='K')
    line = Line(canvas=Canvas(), data=da)
    assert line._unit == 'K'
    assert line._dim == 'xx'
    assert len(line._line.get_xdata()) == da.sizes['xx']
    assert np.allclose(line._line.get_xdata(), da.meta['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values)
    assert line._error is None
    assert not line._mask.get_visible()


def test_line_creation_bin_edges():
    da = data_array(ndim=1, binedges=True)
    line = Line(canvas=Canvas(), data=da)
    assert len(line._line.get_xdata()) == da.sizes['xx'] + 1


def test_line_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._error.has_yerr
    coll = line._error.get_children()[0]
    x = np.array(coll.get_segments())[:, 0, 0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(x, da.meta['xx'].values)
    assert np.allclose(y1, (da.data - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data + sc.stddevs(da.data)).values)


def test_line_hide_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da, errorbars=False)
    assert line._error is None


def test_line_with_mask():
    da = data_array(ndim=1, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.get_visible()


def test_line_update():
    da = data_array(ndim=1)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._line.get_xdata(), da.meta['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values)
    line.update(da * 2.5)
    assert np.allclose(line._line.get_xdata(), da.meta['xx'].values)
    assert np.allclose(line._line.get_ydata(), da.values * 2.5)


def test_line_update_with_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da)
    coll = line._error.get_children()[0]
    x = np.array(coll.get_segments())[:, 0, 0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(x, da.meta['xx'].values)
    assert np.allclose(y1, (da.data - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data + sc.stddevs(da.data)).values)
    new_values = da * 2.5
    new_values.variances = da.variances
    line.update(new_values)
    coll = line._error.get_children()[0]
    y1 = np.array(coll.get_segments())[:, 0, 1]
    y2 = np.array(coll.get_segments())[:, 1, 1]
    assert np.allclose(y1, (da.data * 2.5 - sc.stddevs(da.data)).values)
    assert np.allclose(y2, (da.data * 2.5 + sc.stddevs(da.data)).values)

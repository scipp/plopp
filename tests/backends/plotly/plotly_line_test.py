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


def test_line_with_bin_edges_and_errorbars():
    da = data_array(ndim=1, binedges=True, variances=True)
    line = Line(canvas=Canvas(), data=da)
    assert np.allclose(line._error.x, sc.midpoints(da.meta['xx']).values)


def test_line_hide_errorbars():
    da = data_array(ndim=1, variances=True)
    line = Line(canvas=Canvas(), data=da, errorbars=False)
    assert line._error is None


def test_line_with_mask():
    da = data_array(ndim=1, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.visible


def test_line_with_mask_and_binedges():
    da = data_array(ndim=1, binedges=True, masks=True)
    line = Line(canvas=Canvas(), data=da)
    assert line._mask.visible


def test_line_with_two_masks():
    da = data_array(ndim=1, masks=True)
    da.masks['two'] = da.coords['xx'] > sc.scalar(25, unit='m')
    line = Line(canvas=Canvas(), data=da)
    expected = da.data[da.masks['mask'] | da.masks['two']].values
    y = line._mask.y
    assert np.allclose(y[~np.isnan(y)], expected)


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


def test_line_datetime_binedges_with_errorbars():
    t = np.arange(np.datetime64('2017-03-16T20:58:17'),
                  np.datetime64('2017-03-16T21:15:17'), 20)
    time = sc.array(dims=['time'], values=t)
    v = np.random.rand(time.sizes['time'] - 1)
    da = sc.DataArray(data=sc.array(dims=['time'], values=10 * v, variances=v),
                      coords={'time': time})
    xint = t.astype(int)
    xmid = (0.5 * (xint[1:] + xint[:-1])).astype(int)
    expected = np.array(xmid, dtype=t.dtype)
    line = Line(canvas=Canvas(), data=da)
    # Note that allclose does not work on datetime dtypes
    assert np.allclose(line._error.x.astype(int), expected.astype(int))
